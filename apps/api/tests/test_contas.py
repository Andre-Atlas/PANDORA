import pytest

from pandora_api.dominio.erros import CredenciaisInvalidas, EmailJaCadastrado, SenhaFraca, SessaoInvalida


def test_cadastro_normaliza_email_e_nao_guarda_a_senha(conteiner, repos):
    usuario = conteiner.contas.cadastrar("  Carla@Exemplo.com ", "senha-forte-1")
    assert usuario.email == "carla@exemplo.com"
    assert "senha-forte-1" not in usuario.senha_hash
    assert usuario.senha_hash.startswith("scrypt$")


def test_email_repetido_e_senha_curta(conteiner):
    conteiner.contas.cadastrar("carla@exemplo.com", "senha-forte-1")
    with pytest.raises(EmailJaCadastrado):
        conteiner.contas.cadastrar("CARLA@exemplo.com", "outra-senha-9")
    with pytest.raises(SenhaFraca):
        conteiner.contas.cadastrar("diego@exemplo.com", "curta")


def test_entrar_guarda_so_o_hash_do_token(conteiner, repos):
    conteiner.contas.cadastrar("carla@exemplo.com", "senha-forte-1")
    sessao = conteiner.contas.entrar("carla@exemplo.com", "senha-forte-1")
    _, sessoes, _ = repos
    assert sessao.token not in sessoes.dados
    assert conteiner.contas.usuario_da_sessao(sessao.token).email == "carla@exemplo.com"


def test_credenciais_erradas_nao_revelam_se_o_email_existe(conteiner):
    conteiner.contas.cadastrar("carla@exemplo.com", "senha-forte-1")
    with pytest.raises(CredenciaisInvalidas):
        conteiner.contas.entrar("carla@exemplo.com", "senha-errada-1")
    with pytest.raises(CredenciaisInvalidas):
        conteiner.contas.entrar("ninguem@exemplo.com", "senha-forte-1")


def test_sessao_expira_e_sair_encerra(conteiner, relogio):
    conteiner.contas.cadastrar("carla@exemplo.com", "senha-forte-1")
    sessao = conteiner.contas.entrar("carla@exemplo.com", "senha-forte-1")
    relogio.avancar(hours=25)
    with pytest.raises(SessaoInvalida):
        conteiner.contas.usuario_da_sessao(sessao.token)

    outra = conteiner.contas.entrar("carla@exemplo.com", "senha-forte-1")
    conteiner.contas.sair(outra.token)
    with pytest.raises(SessaoInvalida):
        conteiner.contas.usuario_da_sessao(outra.token)
