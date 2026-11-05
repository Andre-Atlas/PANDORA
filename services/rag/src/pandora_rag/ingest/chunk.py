"""Divisão do texto em chunks.

`estrutural` respeita a unidade jurídica: artigo (caput, parágrafos e incisos juntos),
verbete de súmula e seção de cartilha. `fixo` é o controle da ablação: janelas de
palavras com sobreposição, sem olhar a estrutura.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from pandora_rag.ingest.fontes import Fonte

# Limites em palavras (~1,45 token por palavra em português): mantêm o chunk abaixo de 512 tokens.
MAX_PALAVRAS_ARTIGO = 320
ALVO_PALAVRAS_SECAO = 260
MIN_PALAVRAS_SECAO = 80
MAX_PALAVRAS_BLOCO = 200
SOBREPOSICAO_BLOCO = 60  # só blocos curtos são repetidos como contexto no chunk seguinte
JANELA_FIXA = 300
SOBREPOSICAO_FIXA = 40

ASPAS_ABRE = "“‘\"'"
ASPAS_FECHA = "”’\"'"
RE_ARTIGO = re.compile(r"^[“‘\"'\s]*Art\.?\s*(\d+(?:\.\d+)*)\s*(?:º|°|o\b)?\s*(?:-\s*([A-Z]))?(?![\wÀ-ú])", re.U)
RE_CABECALHO = re.compile(r"^[“‘\"'\s]*Art\.?\s*[\d.]+\s*(?:º|°)?\s*(?:-\s*[A-Z])?\.?\s*", re.U)
RE_ALTERADORA = re.compile(r"\b(?:passa|passam) a vigorar|\bacrescid[oa]s?\b|\bfica(?:m)? acrescid", re.I)
RE_NORMA_ALVO = re.compile(r"((?:Lei(?: Complementar)?|Decreto-Lei|Decreto|Resolução(?: CMN| BCB)?) n[º°o]\s*[\d.]+(?:\s*,\s*de\s+\d{1,2}[º°]?\s+de\s+\w+\s+de\s+\d{4}|\s*,\s*de\s+\d{4})?)", re.I)
RE_ESTRUTURA = re.compile(r"^(LIVRO|PARTE|TÍTULO|CAPÍTULO|SEÇÃO|SUBSEÇÃO)\b", re.I)
RE_SUMULA = re.compile(r"^S[ÚU]MULA\s+(\d+)\s*(\(S[ÚU]MULA CANCELADA\))?\s*VEJA MAIS", re.I)
RE_MARCADOR = re.compile(r"^(\)\s*)?(\(\s*(Revogad[oa]|Vetad[oa]|VETADO|Vig[êe]ncia)[^)]*\)\.?(\s*\(Vig[êe]ncia\))?|(Vig[êe]ncia encerrada\s*)+)$", re.I)
RE_ANOTACAO = re.compile(
    r"\s*\((?:Reda[çc][ãa]o dada|Inclu[íi]d[oa]|Vide|Vig[êe]ncia|Regulament|Produ[çc][ãa]o de efeito|Revogad)[^)]*\)\.?", re.I
)


@dataclass
class Chunk:
    id: str
    fonte_id: str
    texto: str
    artigo: str | None = None
    secao: str | None = None
    pagina: int | None = None
    ordem: int = 0
    estrategia: str = "estrutural"
    citado: bool = False  # artigo entre aspas, inserido em outra norma
    alvo: str | None = None  # norma alterada, quando citado
    descartes: dict = field(default_factory=dict)

    @property
    def palavras(self) -> int:
        return len(self.texto.split())

    @property
    def hash(self) -> str:
        return hashlib.sha256(f"{self.fonte_id}|{self.artigo}|{self.texto}".encode()).hexdigest()


def limpar_anotacoes(texto: str) -> str:
    texto = RE_ANOTACAO.sub("", texto)
    texto = re.sub(r"\(?\s*Vig[êe]ncia encerrada\s*\)?", " ", texto, flags=re.I)
    texto = re.sub(r"[.…]{4,}", "[...]", texto)  # trecho inalterado em leis alteradoras
    return re.sub(r"\s+", " ", texto).strip()


def _sem_aspas(texto: str) -> str:
    return texto.lstrip(ASPAS_ABRE + " ").rstrip(ASPAS_FECHA + " ")


def numero_artigo(texto: str) -> str | None:
    m = RE_ARTIGO.match(texto)
    if not m:
        return None
    return m.group(1).replace(".", "") + (f"-{m.group(2)}" if m.group(2) else "")


def _dividir_artigo(blocos: list[str], limite: int) -> list[list[str]]:
    partes: list[list[str]] = [[]]
    palavras = 0
    for b in blocos:
        n = len(b.split())
        inicio_paragrafo = b.startswith("§") or b.startswith("Parágrafo único")
        if partes[-1] and palavras + n > limite and (inicio_paragrafo or palavras > limite):
            partes.append([])
            palavras = 0
        partes[-1].append(b)
        palavras += n
    return partes


def por_artigo(fonte: Fonte, blocos: list[dict]) -> list[Chunk]:
    chunks: list[Chunk] = []
    secao: str | None = None
    secao_pendente: str | None = None
    atual: dict | None = None
    alvo_atual: str | None = None
    descartes = {"marcadores": 0, "artigos_revogados": 0, "fora_da_lista": 0}
    permitidos = set(fonte.itens) if fonte.itens else None

    def fechar() -> None:
        nonlocal atual
        if not atual:
            return
        bruto = " ".join(atual["blocos"])
        corpo = [limpar_anotacoes(b) for b in atual["blocos"]]
        corpo = [b for b in corpo if b]
        sem_cabecalho = RE_CABECALHO.sub("", " ".join(corpo)).strip(" .")
        revogado = bool(re.search(r"\((Revogad|VETAD)", bruto, re.I)) and len(sem_cabecalho.split()) < 3
        if not corpo or not sem_cabecalho or revogado:
            descartes["artigos_revogados"] += 1
        elif permitidos is not None and atual["numero"] not in permitidos:
            descartes["fora_da_lista"] += 1
        else:
            partes = _dividir_artigo(corpo, MAX_PALAVRAS_ARTIGO)
            for k, parte in enumerate(partes, start=1):
                rotulo = f"Art. {atual['numero']}" if atual["numero"] else None
                texto = "\n".join(parte)
                if k > 1 and rotulo:
                    texto = f"{rotulo} (continuação)\n{texto}"
                sufixo = f"-p{k}" if len(partes) > 1 else ""
                chunks.append(
                    Chunk(
                        id=f"{fonte.id}#{'c' if atual['citado'] else ''}{atual['numero'] or 'preambulo'}{sufixo}",
                        fonte_id=fonte.id,
                        texto=texto,
                        artigo=rotulo,
                        secao=atual["secao"],
                        ordem=len(chunks),
                        citado=atual["citado"],
                        alvo=atual["alvo"],
                    )
                )
        atual = None

    for bloco in blocos:
        t = bloco["t"]
        if RE_MARCADOR.match(t):
            descartes["marcadores"] += 1
            continue
        if RE_ESTRUTURA.match(t) and len(t) < 60:
            fechar()
            secao_pendente = t.title() if t.isupper() else t
            secao = secao_pendente
            continue
        if secao_pendente and atual is None and not RE_ARTIGO.match(t) and len(t) < 110 and not t.endswith((".", ":", ";")):
            secao = f"{secao_pendente} — {t}"
            secao_pendente = None
            continue
        numero = numero_artigo(t)
        if numero:
            fechar()
            atual = {
                "numero": numero,
                "blocos": [_sem_aspas(t)],
                "secao": secao,
                "citado": t.lstrip()[:1] in ASPAS_ABRE,
                "alvo": alvo_atual if t.lstrip()[:1] in ASPAS_ABRE else None,
            }
            if not atual["citado"] and RE_ALTERADORA.search(t) and (m := RE_NORMA_ALVO.search(t)):
                alvo_atual = re.sub(r"\s+", " ", m.group(1)).replace(" ,", ",")
            secao_pendente = None
            continue
        if atual is None:
            atual = {"numero": None, "blocos": [t], "secao": "Preâmbulo", "citado": False, "alvo": None}
        else:
            atual["blocos"].append(_sem_aspas(t) if t.rstrip()[-1:] in ASPAS_FECHA else t)
    fechar()
    if chunks:
        chunks[0].descartes = descartes
    return chunks


def por_sumula(fonte: Fonte, blocos: list[dict]) -> list[Chunk]:
    chunks: list[Chunk] = []
    permitidos = set(fonte.itens) if fonte.itens else None
    atual: dict | None = None

    def fechar() -> None:
        if not atual or atual["cancelada"]:
            return
        if permitidos is not None and atual["numero"] not in permitidos:
            return
        texto = f"Súmula {atual['numero']} do STJ: " + " ".join(atual["corpo"])
        chunks.append(
            Chunk(
                id=f"{fonte.id}#{atual['numero']}",
                fonte_id=fonte.id,
                texto=limpar_anotacoes(texto),
                artigo=f"Súmula {atual['numero']}",
                secao="Súmulas do STJ",
                pagina=atual["pagina"],
                ordem=len(chunks),
            )
        )

    for bloco in blocos:
        m = RE_SUMULA.match(bloco["t"])
        if m:
            fechar()
            atual = {"numero": m.group(1), "cancelada": bool(m.group(2)), "corpo": [], "pagina": bloco["p"]}
        elif atual is not None and not bloco["t"].lower().startswith("enunciados das súmulas"):
            atual["corpo"].append(bloco["t"])
    fechar()
    return sorted(chunks, key=lambda c: -int(c.artigo.split()[1]))


def _eh_titulo(t: str) -> bool:
    if len(t) > 90 or t.endswith((".", ",", ";", ":")) or len(t.split()) > 12:
        return False
    return t.isupper() or bool(re.match(r"^(\d+(\.\d+)*\.?\s+\S|Cap[ií]tulo|M[óo]dulo|Parte|Se[çc][ãa]o|Anexo|Pergunta)", t, re.I))


def _quebrar_bloco_longo(bloco: dict) -> list[dict]:
    """Blocos acima de MAX_PALAVRAS_BLOCO (texto corrido de PDF) são partidos em frases."""
    if len(bloco["t"].split()) <= MAX_PALAVRAS_BLOCO:
        return [bloco]
    frases = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ú“\"(])", bloco["t"])
    partes, atual = [], []
    for f in frases:
        if atual and len(" ".join(atual + [f]).split()) > MAX_PALAVRAS_BLOCO:
            partes.append(" ".join(atual))
            atual = []
        atual.append(f)
    partes.append(" ".join(atual))
    return [{"p": bloco["p"], "t": t} for t in partes]


def por_secao(fonte: Fonte, blocos: list[dict]) -> list[Chunk]:
    chunks: list[Chunk] = []
    blocos = [parte for b in blocos for parte in _quebrar_bloco_longo(b)]
    secao: str | None = None
    buf: list[str] = []
    pagina: int | None = None
    palavras = 0

    def fechar(manter_ultimo: bool = False) -> None:
        nonlocal buf, palavras, pagina
        if not buf:
            return
        texto = "\n".join(buf).strip()
        if len(texto.split()) >= 15:
            chunks.append(
                Chunk(
                    id=f"{fonte.id}#s{len(chunks) + 1}",
                    fonte_id=fonte.id,
                    texto=texto,
                    secao=secao,
                    pagina=pagina,
                    ordem=len(chunks),
                )
            )
        ultimo = buf[-1] if manter_ultimo and len(buf[-1].split()) <= SOBREPOSICAO_BLOCO else None
        buf = [ultimo] if ultimo else []
        palavras = len(ultimo.split()) if ultimo else 0
        pagina = None

    for bloco in blocos:
        t = bloco["t"]
        if _eh_titulo(t):
            if palavras >= MIN_PALAVRAS_SECAO:
                fechar()
            secao = t.title() if t.isupper() else t
            continue
        n = len(t.split())
        if buf and palavras + n > ALVO_PALAVRAS_SECAO and palavras >= MIN_PALAVRAS_SECAO:
            fechar(manter_ultimo=True)
        if pagina is None:
            pagina = bloco["p"]
        buf.append(t)
        palavras += n
    fechar()
    return chunks


def fixo(fonte: Fonte, blocos: list[dict], janela: int = JANELA_FIXA, sobreposicao: int = SOBREPOSICAO_FIXA) -> list[Chunk]:
    """Controle: janelas de palavras sobre o texto corrido, sem estrutura."""
    palavras: list[tuple[str, int | None]] = []
    for b in blocos:
        palavras.extend((w, b["p"]) for w in limpar_anotacoes(b["t"]).split())
    chunks: list[Chunk] = []
    passo = janela - sobreposicao
    for ini in range(0, max(len(palavras), 1), passo):
        trecho = palavras[ini : ini + janela]
        if len(trecho) < 15:
            break
        chunks.append(
            Chunk(
                id=f"{fonte.id}#w{len(chunks) + 1}",
                fonte_id=fonte.id,
                texto=" ".join(w for w, _ in trecho),
                pagina=trecho[0][1],
                ordem=len(chunks),
                estrategia="fixo",
            )
        )
        if ini + janela >= len(palavras):
            break
    return chunks


def garantir_ids_unicos(chunks: list[Chunk]) -> list[Chunk]:
    """Anexos que reiniciam a numeração geram ids repetidos: o 2º recebe ~2, o 3º ~3."""
    vistos: dict[str, int] = {}
    for c in chunks:
        vistos[c.id] = vistos.get(c.id, 0) + 1
        if vistos[c.id] > 1:
            c.id = f"{c.id}~{vistos[c.id]}"
    return chunks


def dividir(fonte: Fonte, blocos: list[dict], estrategia: str = "estrutural") -> list[Chunk]:
    if estrategia == "fixo":
        chunks = fixo(fonte, blocos)
    elif fonte.tipo in ("lei", "decreto", "resolucao"):
        chunks = por_artigo(fonte, blocos)
    elif fonte.tipo == "sumula":
        chunks = por_sumula(fonte, blocos)
    else:
        chunks = por_secao(fonte, blocos)
    return garantir_ids_unicos(chunks)
