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
