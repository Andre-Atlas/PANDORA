from services.ml.apostas.operadoras import carregar_operadoras, verificar_operadora_autorizada

def test_carregar_operadoras():
    operadoras = carregar_operadoras()

    assert len(operadoras) > 0


def test_operadora_possui_cnpj():
    operadoras = carregar_operadoras()

    for operadora in operadoras:
        assert operadora["cnpj"]


def test_operadora_possui_marca():
    operadoras = carregar_operadoras()

    bpx = next(
        op for op in operadoras
        if op["nome"] == "BPX BETS SPORTS GROUP LTDA"
    )

    assert "VAIDEBET" in bpx["marcas"]
    assert "BETPIX365" in bpx["marcas"]
    assert "OBABET" in bpx["marcas"]


def test_operadora_possui_dominio():
    operadoras = carregar_operadoras()

    bpx = next(
        op for op in operadoras
        if op["nome"] == "BPX BETS SPORTS GROUP LTDA"
    )

    assert "vaidebet.bet.br" in bpx["dominios"]

def test_verifica_operadora_autorizada_por_cnpj():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"]
        }
    ]

    resultado = verificar_operadora_autorizada(
        cnpj="12.345.678/0001-90",
        operadoras=operadoras
    )

    assert resultado["encontrada"] is True
    assert resultado["autorizada"] is True
    assert resultado["evidencia"] == "CNPJ exato"


def test_operadora_nao_encontrada_na_base():
    resultado = verificar_operadora_autorizada(
        nome="EMPRESA DESCONHECIDA",
        operadoras=[]
    )

    assert resultado["encontrada"] is False
    assert resultado["autorizada"] is None

def test_verifica_operadora_autorizada_por_dominio():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"]
        }
    ]

    resultado = verificar_operadora_autorizada(
        dominio="https://www.vaidebet.bet.br",
        operadoras=operadoras
    )

    assert resultado["encontrada"] is True
    assert resultado["autorizada"] is True
    assert resultado["evidencia"] == "Domínio exato"


def test_verifica_operadora_autorizada_por_nome():
    operadoras = [
        {
            "nome": "Empresa Exemplo LTDA",
            "cnpj": "12.345.678/0001-90",
            "marca": "VAIDEBET",
            "marcas": ["VAIDEBET"],
            "dominios": ["vaidebet.bet.br"]
        }
    ]

    resultado = verificar_operadora_autorizada(
        nome="VAIDEBET",
        operadoras=operadoras
    )

    assert resultado["encontrada"] is True
    assert resultado["autorizada"] is True
    assert resultado["evidencia"] == "Nome ou marca exatos"