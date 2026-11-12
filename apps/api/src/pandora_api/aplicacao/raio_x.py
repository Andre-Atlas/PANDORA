"""Casos de uso da #72: envio de extrato, transações, correção de categoria e Raio-X."""

from __future__ import annotations

from collections import Counter
from typing import Protocol
from uuid import UUID, uuid4

from pandora_api.dominio.consentimento import Finalidade
from pandora_api.dominio.erros import (
    ArquivoGrandeDemais,
    ArquivoIlegivel,
    ExtratoNaoEncontrado,
    FormatoNaoSuportado,
    TransacaoNaoEncontrada,
)
from pandora_api.dominio.extrato import TAMANHO_MAXIMO_BYTES, Extrato, StatusExtrato
from pandora_api.dominio.raio_x import RaioX, montar_raio_x
from pandora_api.dominio.transacao import Categoria, OrigemCategoria, Transacao, TransacaoLida, mes_local
from pandora_api.portas.ingestao import Classificacao, ClassificadorTransacoes, LeitorExtrato
from pandora_api.portas.repositorios import RepositorioExtratos, RepositorioTransacoes
from pandora_api.portas.servicos import Relogio


class ExigeConsentimento(Protocol):
    """O pedaço de `Consentimentos` que este caso de uso usa."""

    def exigir(self, usuario_id: UUID, finalidade: Finalidade) -> None: ...


class Extratos:
    def __init__(
        self,
        extratos: RepositorioExtratos,
        transacoes: RepositorioTransacoes,
        leitor: LeitorExtrato,
        classificador: ClassificadorTransacoes,
        consentimentos: ExigeConsentimento,
        relogio: Relogio,
    ) -> None:
        self._extratos = extratos
        self._transacoes = transacoes
        self._leitor = leitor
        self._classificador = classificador
        self._consentimentos = consentimentos
        self._relogio = relogio

    def enviar(self, usuario_id: UUID, nome_arquivo: str, conteudo: bytes) -> Extrato:
        """Lê, classifica e guarda. Hoje é síncrono; o status já prevê o processamento em fila."""
        self._consentimentos.exigir(usuario_id, Finalidade.DIAGNOSTICO_FINANCEIRO)
        if len(conteudo) > TAMANHO_MAXIMO_BYTES:
            raise ArquivoGrandeDemais(TAMANHO_MAXIMO_BYTES)

        extrato = Extrato(uuid4(), usuario_id, nome_arquivo, StatusExtrato.PROCESSANDO, self._relogio.agora())
        self._extratos.salvar(extrato)
        try:
            leitura = self._leitor.ler(nome_arquivo, conteudo)
        except (FormatoNaoSuportado, ArquivoIlegivel) as erro:
            extrato = extrato.falhar((str(erro),))
            self._extratos.salvar(extrato)
            return extrato

        novas, repetidas = self._sem_repetidas(usuario_id, leitura.transacoes)
        classificacoes = self._classificador.classificar(novas)
        transacoes = [_transacao(lida, c) for lida, c in zip(novas, classificacoes, strict=True)]
        self._transacoes.adicionar(usuario_id, transacoes)

        avisos = list(leitura.avisos)
        if repetidas:
            avisos.append(f"{repetidas} transação(ões) já estavam importadas e não entraram de novo.")
        extrato = extrato.concluir(len(transacoes), tuple(avisos))
        self._extratos.salvar(extrato)
        return extrato

    def situacao(self, usuario_id: UUID, extrato_id: UUID) -> Extrato:
        extrato = self._extratos.por_id(usuario_id, extrato_id)
        if extrato is None:
            raise ExtratoNaoEncontrado()
        return extrato

    def _sem_repetidas(self, usuario_id: UUID, lidas: tuple[TransacaoLida, ...]) -> tuple[list[TransacaoLida], int]:
        """Descarta o que já foi importado, contando repetições.

        Dois cafés iguais no mesmo dia são duas transações. Se o mesmo extrato
        vier de novo, as duas já existem e nenhuma entra outra vez.
        """
        meses = {mes_local(t.data_hora) for t in lidas}
        ja_importadas = Counter(_chave(t) for mes in meses for t in self._transacoes.do_mes(usuario_id, mes))
        novas: list[TransacaoLida] = []
        for lida in lidas:
            chave = _chave(lida)
            if ja_importadas[chave] > 0:
                ja_importadas[chave] -= 1
            else:
                novas.append(lida)
        return novas, len(lidas) - len(novas)


def _chave(t: Transacao | TransacaoLida) -> tuple:
    return (t.conta_id, t.data_hora, t.valor_centavos, t.descricao_mascarada)


def _transacao(lida: TransacaoLida, c: Classificacao) -> Transacao:
    return Transacao(
        id=uuid4(),
        conta_id=lida.conta_id,
        data_hora=lida.data_hora,
        valor_centavos=lida.valor_centavos,
        forma_pagamento=lida.forma_pagamento,
        descricao_mascarada=lida.descricao_mascarada,
        mcc=lida.mcc,
        categoria=c.categoria,
        origem_categoria=OrigemCategoria.MODELO,
        confianca_categoria=c.confianca,
        versao_modelo=c.versao_modelo,
        essencial=c.essencial,
        parcela=lida.parcela,
    )


class Transacoes:
    def __init__(self, repositorio: RepositorioTransacoes, classificador: ClassificadorTransacoes) -> None:
        self._repo = repositorio
        self._classificador = classificador

    def listar(
        self, usuario_id: UUID, mes: str | None, categoria: Categoria | None, pagina: int, por_pagina: int
    ) -> tuple[list[Transacao], int]:
        return self._repo.listar(usuario_id, mes, categoria, (pagina - 1) * por_pagina, por_pagina)

    def corrigir_categoria(self, usuario_id: UUID, transacao_id: UUID, categoria: Categoria) -> Transacao:
        transacao = self._repo.por_id(usuario_id, transacao_id)
        if transacao is None:
            raise TransacaoNaoEncontrada()
        corrigida = transacao.corrigida_pela_pessoa(categoria, self._classificador.essencial(transacao, categoria))
        self._repo.atualizar(usuario_id, corrigida)
        return corrigida

    def raio_x(self, usuario_id: UUID, mes: str) -> RaioX:
        return montar_raio_x(mes, self._repo.do_mes(usuario_id, mes))
