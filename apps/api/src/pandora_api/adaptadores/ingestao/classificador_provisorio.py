"""Classificador PROVISÓRIO, até o modelo da Mariana (#68) ser servido (#83).

Não é modelo: usa o rótulo do arquivo quando ele existe (só o dataset
sintético da #51 traz) e, sem rótulo, uma tabela pequena de MCC. O que não
casa vira TRANSFERENCIA, que fica fora dos gastos do Raio-X, para não inflar
nenhuma categoria por chute. A `versao_modelo` deixa claro de onde veio.

Essencialidade (Mínimo Existencial) por categoria: é uma aproximação das
regras do dataset (`regras_essencialidade.csv`), que olham também subtipo,
horário e valor.
"""

from __future__ import annotations

from collections.abc import Sequence

from pandora_api.dominio.transacao import Categoria, Transacao, TransacaoLida
from pandora_api.portas.ingestao import Classificacao

VERSAO_ROTULO = "provisorio-rotulo-do-arquivo"
VERSAO_REGRAS = "provisorio-regras-mcc"

CATEGORIAS_ESSENCIAIS = frozenset(
    {Categoria.MORADIA, Categoria.UTILIDADES, Categoria.ALIMENTACAO, Categoria.SAUDE, Categoria.EDUCACAO}
)

POR_MCC = {
    **dict.fromkeys(("5411", "5412", "5422", "5441", "5451", "5462", "5499"), Categoria.ALIMENTACAO),
    **dict.fromkeys(("5812", "5813", "5814", "7832", "7841"), Categoria.LAZER),
    **dict.fromkeys(("4111", "4121", "4131", "5541", "5542", "7523"), Categoria.TRANSPORTE),
    **dict.fromkeys(("5912", "8011", "8021", "8043", "8062", "8071", "8099"), Categoria.SAUDE),
    **dict.fromkeys(("4814", "4899", "4900"), Categoria.UTILIDADES),
    **dict.fromkeys(("6513",), Categoria.MORADIA),
    **dict.fromkeys(("8211", "8220", "8241", "8244", "8299"), Categoria.EDUCACAO),
    **dict.fromkeys(("7995",), Categoria.APOSTAS_BETS),
}
PALAVRAS_RENDA = ("SALARIO", "SALÁRIO", "PROVENTO", "PAGAMENTO FOLHA", "RESCISAO", "RESCISÃO", "BENEFICIO INSS")


class ClassificadorProvisorio:
    def classificar(self, transacoes: Sequence[TransacaoLida]) -> list[Classificacao]:
        return [self._uma(t) for t in transacoes]

    def essencial(self, transacao: Transacao, categoria: Categoria) -> bool:
        return transacao.valor_centavos < 0 and categoria in CATEGORIAS_ESSENCIAIS

    def _uma(self, t: TransacaoLida) -> Classificacao:
        if t.categoria_no_arquivo is not None:
            essencial = t.essencial_no_arquivo
            if essencial is None:
                essencial = t.valor_centavos < 0 and t.categoria_no_arquivo in CATEGORIAS_ESSENCIAIS
            return Classificacao(t.categoria_no_arquivo, None, VERSAO_ROTULO, essencial)

        if t.valor_centavos > 0 and any(p in t.descricao_mascarada.upper() for p in PALAVRAS_RENDA):
            categoria = Categoria.RENDA
        else:
            categoria = POR_MCC.get(t.mcc or "", Categoria.TRANSFERENCIA)
        essencial = t.valor_centavos < 0 and categoria in CATEGORIAS_ESSENCIAIS
        return Classificacao(categoria, None, VERSAO_REGRAS, essencial)
