"""Pipeline de voz local PT-BR (PyAV + faster-whisper small + Luciana/say TTS) com auditoria RNF01/RNF02."""
from __future__ import annotations

import io
import logging
import re
import shutil
import subprocess
import tempfile
import wave
from collections.abc import Callable
from pathlib import Path
from typing import Any

import av
import numpy as np

from pandora_rag.agents.artifact_store import ArtifactStore
from pandora_rag.agents.models import EstadoMultiagente, ReferenciaMidia
from pandora_rag.generate.pii import mascarar

logger = logging.getLogger(__name__)

_CACHE_WHISPER: dict[str, Any] = {}
_RE_CITACAO_INLINE = re.compile(r"\[\d+\]")
_RE_URL = re.compile(r"https?://\S+")

_SUBSTITUICOES_VOZ_PTBR: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\br\$\s*(\d+)", re.IGNORECASE), r"R$ \1"),
    (re.compile(r"\bpix\b", re.IGNORECASE), "Pix"),
    (re.compile(r"\bmed\b", re.IGNORECASE), "MED"),
    (re.compile(r"\bcvm\b", re.IGNORECASE), "CVM"),
    (re.compile(r"\bcvv\b", re.IGNORECASE), "CVV"),
    (re.compile(r"\b(\d+)\s+por\s+cento\b", re.IGNORECASE), r"\1%"),
)


def decodificar_audio_pyav(audio_bytes: bytes, taxa_alvo: int = 16000) -> np.ndarray:
    """Decodifica WAV/MP3/M4A/OGG em memória via PyAV para float32 mono 16 kHz (sem ffmpeg no PATH)."""
    resampler = av.AudioResampler(format="flt", layout="mono", rate=taxa_alvo)
    blocos: list[np.ndarray] = []

    with av.open(io.BytesIO(audio_bytes)) as container:
        stream = next((s for s in container.streams if s.type == "audio"), None)
        if stream is None:
            raise ValueError("Arquivo de áudio não contém faixa de áudio legível.")
        for frame in container.decode(stream):
            for reamostrado in resampler.resample(frame):
                arr = reamostrado.to_ndarray()
                blocos.append(arr.reshape(-1).astype(np.float32))
        for reamostrado in resampler.resample(None):
            arr = reamostrado.to_ndarray()
            blocos.append(arr.reshape(-1).astype(np.float32))

    if not blocos:
        return np.zeros(0, dtype=np.float32)
    sinal = np.concatenate(blocos).astype(np.float32)
    return np.clip(sinal, -1.0, 1.0)


def normalizar_transcricao_financeira_ptbr(texto: str) -> str:
    """Normaliza termos financeiros falados em PT-BR e aplica máscara de PII (RNF01)."""
    limpo = re.sub(r"\s+", " ", texto).strip()
    for padrao, subst in _SUBSTITUICOES_VOZ_PTBR:
        limpo = padrao.sub(subst, limpo)
    mascarado, _ = mascarar(limpo)
    return mascarado


def _obter_whisper_model(modelo: str = "small") -> Any:
    if modelo not in _CACHE_WHISPER:
        from faster_whisper import WhisperModel

        _CACHE_WHISPER[modelo] = WhisperModel(modelo, device="cpu", compute_type="int8")
    return _CACHE_WHISPER[modelo]


class TranscritorVoz:
    """Transcritor PT-BR local usando faster-whisper (small, int8) ou backend injetável."""

    def __init__(
        self,
        modelo: str = "small",
        backend_fn: Callable[[bytes], str] | None = None,
    ) -> None:
        self.modelo = modelo
        self._backend_fn = backend_fn

    def transcrever_bytes(self, audio_bytes: bytes) -> str:
        """Transcreve áudio em PT-BR e devolve texto normalizado e sem PII."""
        if self._backend_fn is not None:
            bruto = self._backend_fn(audio_bytes)
            return normalizar_transcricao_financeira_ptbr(bruto)

        sinal = decodificar_audio_pyav(audio_bytes, taxa_alvo=16000)
        if sinal.size == 0:
            return ""
        whisper = _obter_whisper_model(self.modelo)
        segmentos, _ = whisper.transcribe(
            sinal,
            language="pt",
            vad_filter=True,
            beam_size=1,
        )
        texto = " ".join(seg.text.strip() for seg in segmentos if seg.text and seg.text.strip())
        return normalizar_transcricao_financeira_ptbr(texto)


def compilar_resumo_falado_tts(estado: EstadoMultiagente) -> str:
    """Compila resumo claro para voz (35-55 palavras) a partir do rascunho aprovado pelo Compliance."""
    if estado.veredito and estado.veredito.crise_acionada:
        return (
            "Você não precisa enfrentar isso sozinho. Pause agora qualquer decisão financeira e ligue "
            "gratuitamente para o CVV no número 188, atendimento 24 horas e sigiloso, ou procure o CAPS AD."
        )
    if estado.inspecao_fraude and estado.inspecao_fraude.fraude_detectada:
        return (
            "Atenção: pare e não pague este boleto nem faça novas transferências. Detectamos sinais de "
            "fraude no documento analisado. Se você já enviou um Pix, acione o Mecanismo Especial de "
            "Devolução no aplicativo do seu banco em até 80 dias."
        )
    if estado.veredito and estado.veredito.bloqueio_cvm_acionado:
        return (
            "Pelas regras da CVM, eu não faço recomendação específica de ativos ou bancos. "
            "Compare sempre liquidez diária, proteção do FGC ou Tesouro Nacional e rendimento atrelado à Selic ou ao CDI."
        )

    base = estado.resposta_final or estado.rascunho_resposta or ""
    sem_urls = _RE_URL.sub("", base)
    sem_cit = _RE_CITACAO_INLINE.sub("", sem_urls)
    limpo = re.sub(r"\s+", " ", sem_cit.replace("\n", " ")).strip()
    palavras = limpo.split()
    if len(palavras) > 55:
        limpo = " ".join(palavras[:55]).rstrip(",;:") + "."
    texto_seguro, _ = mascarar(limpo)
    return texto_seguro


def _gerar_wav_pcm_silencio(duracao_s: float = 0.4, taxa: int = 22050) -> bytes:
    amostras = np.zeros(int(duracao_s * taxa), dtype=np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(taxa)
        wf.writeframes(amostras.tobytes())
    return buf.getvalue()


class SintetizadorVoz:
    """Sintetiza resposta falada em PT-BR via macOS `say -v Luciana` ou fallback WAV PCM."""

    def __init__(self, voz: str = "Luciana") -> None:
        self.voz = voz
        self._say_bin = shutil.which("say")

    def sintetizar_para_bytes(self, texto: str) -> bytes:
        texto_limpo, _ = mascarar(texto.strip())
        texto_limpo = texto_limpo.lstrip("-–— ").strip()
        if not texto_limpo:
            return _gerar_wav_pcm_silencio()

        if self._say_bin:
            with tempfile.TemporaryDirectory(prefix="pandora_tts_") as tmp:
                destino = Path(tmp) / "saida.wav"
                try:
                    subprocess.run(
                        [
                            self._say_bin,
                            "-v",
                            self.voz,
                            "-o",
                            str(destino),
                            "--data-format=LEI16@22050",
                            texto_limpo,
                        ],
                        check=True,
                        capture_output=True,
                        timeout=15,
                    )
                    if destino.exists() and destino.stat().st_size > 44:
                        return destino.read_bytes()
                except (OSError, subprocess.SubprocessError) as exc:
                    logger.warning("Falha no /usr/bin/say; usando fallback WAV PCM: %s", exc)

        return _gerar_wav_pcm_silencio()

    def sintetizar_no_store(self, texto: str, store: ArtifactStore) -> ReferenciaMidia:
        wav_bytes = self.sintetizar_para_bytes(texto)
        return store.registrar_bytes(
            wav_bytes,
            tipo="audio_tts_saida",
            nome_original="resposta_elpis.wav",
            mime_type="audio/wav",
        )
