"""ArtifactStore efêmero local (Pass-by-Reference) para mídia multimodal sem State Bloat (RNF01)."""
from __future__ import annotations

import hashlib
import io
import re
import shutil
import tempfile
import threading
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from PIL import Image, ImageOps

from pandora_rag.agents.models import ReferenciaMidia, TipoMidia

MAX_ARTEFATO_BYTES = 25 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 40_000_000
_RE_ARTEFATO_ID = re.compile(r"^[a-f0-9]{32}$")
_MIMES_IMAGEM_PERMITIDOS = {"image/png", "image/jpeg", "image/webp"}

_RE_NOME_SEGURO = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitizar_nome(nome: str) -> str:
    limpo = _RE_NOME_SEGURO.sub("_", Path(nome).name).strip("._")
    return (limpo or "artefato")[:128]


def _remover_exif_imagem(dados: bytes, mime_type: str) -> tuple[bytes, str]:
    """Re-codifica imagem sem metadados EXIF/GPS (fail-closed), preservando resolução."""
    if mime_type not in _MIMES_IMAGEM_PERMITIDOS:
        raise ValueError(f"Tipo de imagem não suportado: {mime_type}")
    try:
        with (
            Image.open(io.BytesIO(dados), formats=("PNG", "JPEG", "WEBP")) as img,
            closing(ImageOps.exif_transpose(img)) as corrigida,
        ):
            buf = io.BytesIO()
            if mime_type == "image/png":
                fmt, mime_final = "PNG", "image/png"
                corrigida.save(buf, format=fmt)
            else:
                fmt, mime_final = "JPEG", "image/jpeg"
                if corrigida.mode not in ("RGB", "L"):
                    with closing(corrigida.convert("RGB")) as conv:
                        conv.save(buf, format=fmt)
                else:
                    corrigida.save(buf, format=fmt)
            return buf.getvalue(), mime_final
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Arquivo de imagem inválido ou corrompido.") from exc


@dataclass
class _EntradaStore:
    caminho: Path
    expira_em: float
    mime_type: str


class ArtifactStore:
    """Armazena mídia bruta em diretório efêmero isolado (0o700) fora do EstadoMultiagente."""

    def __init__(self, diretorio_base: Path | None = None, ttl_s: int = 900) -> None:
        if diretorio_base is None:
            self._dir = Path(tempfile.mkdtemp(prefix="pandora_midia_"))
            self._criado_internamente = True
        else:
            if diretorio_base.is_symlink():
                raise ValueError("diretorio_base não pode ser symlink.")
            diretorio_base.mkdir(parents=True, exist_ok=True, mode=0o700)
            self._dir = diretorio_base
            self._criado_internamente = False
        self._dir.chmod(0o700)
        self.ttl_s = max(1, ttl_s)
        self._lock = threading.Lock()
        self._itens: dict[str, _EntradaStore] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.expurgar_tudo()

    @property
    def diretorio(self) -> Path:
        """Retorna o diretório efêmero isolado do ArtifactStore."""
        return self._dir

    def _limpar_expirados(self) -> None:
        agora = time.monotonic()
        expirados = [aid for aid, ent in self._itens.items() if ent.expira_em <= agora]
        for aid in expirados:
            ent = self._itens.pop(aid)
            ent.caminho.unlink(missing_ok=True)

    def registrar_bytes(
        self,
        dados: bytes,
        *,
        tipo: TipoMidia,
        nome_original: str,
        mime_type: str,
    ) -> ReferenciaMidia:
        """Grava artefato em disco seguro (removendo EXIF se imagem) e devolve ReferenciaMidia."""
        if len(dados) > MAX_ARTEFATO_BYTES:
            raise ValueError(
                f"Artefato excede o limite máximo de {MAX_ARTEFATO_BYTES} bytes (recebido: {len(dados)})."
            )
        if mime_type.startswith("image/"):
            conteudo, mime_final = _remover_exif_imagem(dados, mime_type)
        else:
            conteudo, mime_final = dados, mime_type
        artefato_id = uuid.uuid4().hex
        digest = hashlib.sha256(conteudo).hexdigest()
        destino = self._dir / f"{artefato_id}.bin"
        with self._lock:
            self._limpar_expirados()
            destino.write_bytes(conteudo)
            destino.chmod(0o600)
            self._itens[artefato_id] = _EntradaStore(
                caminho=destino,
                expira_em=time.monotonic() + self.ttl_s,
                mime_type=mime_final,
            )
        return ReferenciaMidia(
            artefato_id=artefato_id,
            tipo=tipo,
            nome_original_sanitizado=_sanitizar_nome(nome_original),
            mime_type=mime_final,
            sha256=digest,
            tamanho_bytes=len(conteudo),
        )

    def registrar_arquivo(
        self,
        caminho: Path,
        *,
        tipo: TipoMidia,
        mime_type: str | None = None,
    ) -> ReferenciaMidia:
        """Lê um arquivo local regular (até MAX_ARTEFATO_BYTES) e registra no ArtifactStore."""
        if caminho.is_symlink() or not caminho.is_file():
            raise FileNotFoundError(f"Arquivo de mídia inválido ou inexistente: {caminho}")
        tamanho = caminho.stat().st_size
        if tamanho > MAX_ARTEFATO_BYTES:
            raise ValueError(
                f"Arquivo excede o limite máximo de {MAX_ARTEFATO_BYTES} bytes (tamanho: {tamanho})."
            )
        ext = caminho.suffix.lower()
        mime = mime_type or {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".ofx": "application/x-ofx",
            ".csv": "text/csv",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
        }.get(ext, "application/octet-stream")
        return self.registrar_bytes(
            caminho.read_bytes(),
            tipo=tipo,
            nome_original=caminho.name,
            mime_type=mime,
        )

    def _obter_entrada(self, artefato_id: str) -> _EntradaStore:
        if not _RE_ARTEFATO_ID.fullmatch(artefato_id):
            raise ValueError("artefato_id inválido.")
        with self._lock:
            self._limpar_expirados()
            ent = self._itens.get(artefato_id)
            if ent is None or not ent.caminho.exists():
                raise FileNotFoundError(f"Artefato multimodal expirado ou inexistente: {artefato_id}")
            return ent

    def obter_bytes(self, artefato_id: str) -> bytes:
        """Recupera os bytes originais (resolução cheia para zxing-cpp / pdfplumber / PyAV)."""
        return self._obter_entrada(artefato_id).caminho.read_bytes()

    def obter_caminho(self, artefato_id: str) -> Path:
        """Retorna o caminho seguro do artefato armazenado."""
        return self._obter_entrada(artefato_id).caminho

    def obter_imagem_vlm_bytes(self, artefato_id: str, max_lado: int = 1024) -> bytes:
        """Devolve versão redimensionada da imagem para acelerar inferência VLM mantendo aspect ratio."""
        bruto = self.obter_bytes(artefato_id)
        with Image.open(io.BytesIO(bruto)) as img:
            if max(img.size) <= max_lado:
                return bruto
            with closing(img.copy()) as copia:
                copia.thumbnail((max_lado, max_lado), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                if copia.mode not in ("RGB", "L"):
                    with closing(copia.convert("RGB")) as conv:
                        conv.save(buf, format="JPEG", quality=88)
                else:
                    copia.save(buf, format="JPEG", quality=88)
                return buf.getvalue()

    def expurgar_tudo(self) -> int:
        """Apaga todos os artefatos armazenados (conformidade LGPD / DELETE /eu/dados)."""
        with self._lock:
            qtd = len(self._itens)
            for ent in list(self._itens.values()):
                ent.caminho.unlink(missing_ok=True)
            self._itens.clear()
        if self._criado_internamente and self._dir.exists():
            shutil.rmtree(self._dir, ignore_errors=True)
        return qtd
