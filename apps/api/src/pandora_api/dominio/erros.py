class ErroDominio(Exception):
    """Base dos erros de regra de negócio."""


class EmailJaCadastrado(ErroDominio):
    pass


class CredenciaisInvalidas(ErroDominio):
    pass


class SessaoInvalida(ErroDominio):
    pass


class SenhaFraca(ErroDominio):
    pass


class ConsentimentoNecessario(ErroDominio):
    def __init__(self, finalidade: str) -> None:
        super().__init__(f"Consentimento ausente para: {finalidade}")
        self.finalidade = finalidade


class ConsentimentoNaoEncontrado(ErroDominio):
    pass


class AssistenteIndisponivel(ErroDominio):
    """O serviço de respostas (RAG) não respondeu a tempo ou devolveu algo inesperado."""


class LicaoNaoEncontrada(ErroDominio):
    pass


class PerguntaInvalida(ErroDominio):
    """Índice de pergunta ou de opção fora do intervalo da lição."""


class ExtratoNaoEncontrado(ErroDominio):
    pass


class TransacaoNaoEncontrada(ErroDominio):
    pass


class ArquivoGrandeDemais(ErroDominio):
    def __init__(self, limite_bytes: int) -> None:
        super().__init__(f"O limite é de {limite_bytes // (1024 * 1024)} MB por arquivo.")


class FormatoNaoSuportado(ErroDominio):
    """A ingestão não sabe ler este tipo de arquivo (ainda)."""


class ArquivoIlegivel(ErroDominio):
    """O arquivo tem um formato conhecido, mas o conteúdo não dá para ler."""
