
from services.ml.apostas.detector import detectar_aposta


def test_mcc_7995_identifica_aposta():
    resultado = detectar_aposta(
        mcc=7995,
        descricao="COMPRA ONLINE",
        operadoras=[]
    )

    assert resultado["is_bet"] is True
    assert any(e["tipo"] == "mcc" for e in resultado["evidencias"])


def test_nome_da_operadora_identifica_aposta():
    resultado = detectar_aposta(
        mcc=5999,
        descricao="PAGAMENTO BETANO",
        operadoras=["Betano"]
    )

    assert resultado["is_bet"] is True
    assert any(e["tipo"] == "operadora" for e in resultado["evidencias"])


def test_descricao_sem_evidencias_nao_identifica_aposta():
    resultado = detectar_aposta(
        mcc=5999,
        descricao="COMPRA DE ROUPAS",
        operadoras=["Betano"]
    )

    assert resultado["is_bet"] is False
    assert resultado["evidencias"] == []


def test_mcc_pode_ser_string():
    resultado = detectar_aposta(
        mcc="7995",
        descricao="PAGAMENTO",
        operadoras=[]
    )

    assert resultado["is_bet"] is True
    
def test_normaliza_acentos_e_pontuacao():
    resultado = detectar_aposta(
        mcc=5999,
        descricao="PAGAMENTO BETÁNO*ONLINE",
        operadoras=["Betano"]
    )

    assert resultado["is_bet"] is True
    assert resultado["evidencias"][0]["tipo"] == "operadora"

def test_detecta_marca_da_base_oficial():
    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA VAIDEBET",
    )

    assert resultado["is_bet"] is True

def test_nao_identifica_marca_dentro_de_outra_palavra():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"],
        }
    ]

    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA VAIDEBETARIA",
        operadoras=operadoras,
    )

    assert resultado["is_bet"] is False

def test_detecta_marca_secundaria_da_operadora():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET", "BETPIX365", "OBABET"],
            "dominios": [
                "vaidebet.bet.br",
                "betpix365.bet.br",
                "obabet.bet.br",
            ],
        }
    ]

    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA OBABET",
        operadoras=operadoras,
    )

    assert resultado["is_bet"] is True

def test_identifica_aposta_por_cnpj():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"],
        }
    ]

    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA ONLINE",
        cnpj="12345678000190",
        operadoras=operadoras,
    )

    assert resultado["is_bet"] is True

def test_identifica_aposta_por_dominio():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": [
                "vaidebet.bet.br",
                "obabet.bet.br",
            ],
        }
    ]

    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA ONLINE",
        dominio="vaidebet.bet.br",
        operadoras=operadoras,
    )

    assert resultado["is_bet"] is True
    assert any(
        evidencia["tipo"] == "dominio"
        for evidencia in resultado["evidencias"]
    )

def test_detector_retorna_status_de_autorizacao():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"]
        }
    ]

    resultado = detectar_aposta(
        mcc="0000",
        descricao="COMPRA ONLINE",
        cnpj="12.345.678/0001-90",
        operadoras=operadoras
    )

    assert resultado["is_bet"] is True
    assert resultado["autorizacao"]["encontrada"] is True
    assert resultado["autorizacao"]["autorizada"] is True
    assert resultado["autorizacao"]["evidencia"] == "CNPJ exato"

def test_aposta_com_operadora_nao_encontrada_na_base():
    resultado = detectar_aposta(
        mcc="7995",
        descricao="COMPRA ONLINE",
        operadoras=[]
    )

    assert resultado["is_bet"] is True
    assert resultado["autorizacao"]["encontrada"] is False
    assert resultado["autorizacao"]["autorizada"] is None