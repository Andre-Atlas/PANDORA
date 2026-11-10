
import pytest

from services.ml.classificador.baseline import (
    classificar_transacao,
    normalizar,
    VERSAO,
)

def test_normalizar_remove_acentos_e_caracteres_especiais():
    resultado = normalizar("Farmácia São João!")

    assert resultado == "FARMACIA SAO JOAO "


def test_classificar_aposta_pelo_mcc():
    tx = {
        "transaction_id": "tx-001",
        "description_masked": "COMPRA ESTABELECIMENTO",
        "mcc": "7995",
    }

    resultado = classificar_transacao(tx)

    assert resultado["saida"]["categoria"] == "APOSTAS_BETS"
    assert resultado["confianca"] == 0.95
    assert resultado["evidencia"][0]["regra"] == "mcc_7995"


def test_classificar_aposta_pela_descricao():
    tx = {
        "transaction_id": "tx-002",
        "description_masked": "PAGAMENTO BET BR",
        "mcc": "0000",
    }

    resultado = classificar_transacao(tx)

    assert resultado["saida"]["categoria"] == "APOSTAS_BETS"


def test_classificar_renda():
    tx = {
        "transaction_id": "tx-003",
        "description_masked": "CREDITO SALARIO MENSAL",
        "mcc": "0000",
    }

    resultado = classificar_transacao(tx)

    assert resultado["saida"]["categoria"] == "RENDA"


def test_classificar_fraude_especifica():
    tx = {
        "transaction_id": "tx-004",
        "description_masked": "PIX ENVIADO PESSOA FISICA *** OUTLET",
        "mcc": "0000",
    }

    resultado = classificar_transacao(tx)

    assert resultado["saida"]["categoria"] == "FRAUDE_SUSPEITA"


def test_transacao_sem_regra_retorna_nao_classificado():
    tx = {
        "transaction_id": "tx-005",
        "description_masked": "TRANSACAO DESCONHECIDA XYZ",
        "mcc": "0000",
    }

    resultado = classificar_transacao(tx)

    assert resultado["saida"]["categoria"] == "NAO_CLASSIFICADO"
    assert resultado["confianca"] == 0.0
    assert resultado["evidencia"] == []


def test_estrutura_da_resposta():
    tx = {
        "transaction_id": "tx-006",
        "description_masked": "SUPERMERCADO",
        "mcc": "0000",
    }

    resultado = classificar_transacao(tx)

    assert resultado["transacao_id"] == "tx-006"
    assert resultado["modelo"] == "classificador"
    assert resultado["versao"] == VERSAO
    assert "categoria" in resultado["saida"]
    assert isinstance(resultado["confianca"], float)
    assert isinstance(resultado["evidencia"], list)
