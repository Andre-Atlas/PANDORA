"""Erros da ingestão. As mensagens podem ir para a pessoa e para o log: nunca carregam o conteúdo do arquivo."""


class ErroDeIngestao(Exception):
    pass


class FormatoNaoSuportado(ErroDeIngestao):
    pass


class ArquivoIlegivel(ErroDeIngestao):
    pass
