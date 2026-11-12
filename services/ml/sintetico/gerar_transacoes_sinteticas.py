
from pathlib import Path
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


# --------------------------------------------------
# CONFIGURAÇÕES
# --------------------------------------------------

SEMENTE = 42
QUANTIDADE_POR_CATEGORIA = 100

ROOT = Path(__file__).resolve().parents[3]

ARQUIVO_ORIGINAL = (
    ROOT
    / "docs/evidencias/datasets/"
    / "amostra_transacoes_sinteticas_personas.csv"
)

ARQUIVO_SAIDA = (
    ROOT
    / "docs/evidencias/datasets/"
    / "transacoes_sinteticas_expandidas.csv"
)

CATEGORIAS = [
    "RENDA",
    "MORADIA",
    "ALIMENTACAO",
    "DIVIDA_JUROS",
    "APOSTAS_BETS",
    "FRAUDE_SUSPEITA",
    "INVESTIMENTO",
    "TRANSPORTE",
    "COMPRAS_IMPULSO",
    "SAUDE",
]

PERSONAS = [
    "carla_34",
    "diego_24",
    "antonio_67",
    "mariana_28",
    "rosangela_43",
    "rafael_39",
    "lucas_19",
    "fernanda_46",
    "patricia_53",
    "julia_31",
]

MEIOS_PAGAMENTO = [
    "PIX",
    "CREDIT_CARD",
    "DEBIT_CARD",
    "BOLETO",
    "DIRECT_DEBIT",
]


# --------------------------------------------------
# EXEMPLOS DE TRANSAÇÕES POR CATEGORIA
# Cada item contém descrição, MCC e meios possíveis.
# --------------------------------------------------

PADROES = {
    "RENDA": [
        ("SALARIO EMPRESA ALFA", "6012"),
        ("PAGAMENTO SALARIAL", "6012"),
        ("RECEBIMENTO CLIENTE", "4829"),
        ("TRANSFERENCIA RECEBIDA", "4829"),
        ("PAGAMENTO SERVICO PRESTADO", "7399"),
        ("REPASSE TRABALHO AUTONOMO", "6012"),
        ("RECEBIMENTO FREELANCE", "4829"),
        ("BENEFICIO SOCIAL RECEBIDO", "6012"),
    ],

    "MORADIA": [
        ("PAGAMENTO ALUGUEL", "6513"),
        ("CONDOMINIO RESIDENCIAL", "6513"),
        ("CONTA DE ENERGIA", "4900"),
        ("CONTA DE AGUA", "4900"),
        ("SERVICO DE GAS RESIDENCIAL", "4900"),
        ("PAGAMENTO IMOBILIARIA", "6513"),
        ("MANUTENCAO RESIDENCIAL", "1520"),
        ("INTERNET RESIDENCIAL", "4814"),
    ],

    "ALIMENTACAO": [
        ("SUPERMERCADO BOM PRECO", "5411"),
        ("MERCADO CENTRAL", "5411"),
        ("HORTIFRUTI VERDE VIDA", "5499"),
        ("PADARIA DO BAIRRO", "5462"),
        ("ACOUgue E MERCEARIA", "5422"),
        ("COMPRA DE ALIMENTOS", "5411"),
        ("ATACADO ALIMENTAR", "5411"),
        ("FEIRA LIVRE", "5499"),
    ],

    "DIVIDA_JUROS": [
        ("PAGAMENTO FATURA CARTAO", "6012"),
        ("JUROS CARTAO CREDITO", "6012"),
        ("PARCELA EMPRESTIMO", "6012"),
        ("PAGAMENTO CHEQUE ESPECIAL", "6012"),
        ("ENCARGOS FINANCEIROS", "6012"),
        ("PARCELAMENTO DE FATURA", "6012"),
        ("PAGAMENTO CREDITO PESSOAL", "6012"),
        ("TARIFA E JUROS BANCARIOS", "6012"),
    ],

    "APOSTAS_BETS": [
        ("BETX PAGAMENTO", "7995"),
        ("PAGBET APOSTA ONLINE", "7995"),
        ("JOGO ONLINE DE APOSTAS", "7995"),
        ("PIX PARA PLATAFORMA BET", "7995"),
        ("APOSTA ESPORTIVA ONLINE", "7995"),
        ("BET GAMES PAGAMENTO", "7995"),
        ("RECARGA PLATAFORMA DE APOSTAS", "7995"),
        ("TRANSFERENCIA OPERADORA BET", "7995"),
    ],

    "FRAUDE_SUSPEITA": [
        ("PIX ENVIADO DESTINATARIO NOVO", "4829"),
        ("TRANSFERENCIA LOJA DESCONHECIDA", "4829"),
        ("PAGAMENTO BOLETO SUSPEITO", "6012"),
        ("PIX ENVIADO PARA OUTLET", "4829"),
        ("COMPRA LINK DE PAGAMENTO", "5999"),
        ("TRANSFERENCIA BENEFICIARIO NOVO", "4829"),
        ("PAGAMENTO SITE DESCONHECIDO", "5999"),
        ("PIX PARA CONTA NAO RECONHECIDA", "4829"),
    ],

    "INVESTIMENTO": [
        ("APLICACAO RENDA FIXA", "6211"),
        ("INVESTIMENTO CDB", "6211"),
        ("APORTE EM TESOURO DIRETO", "6211"),
        ("APLICACAO FUNDO INVESTIMENTO", "6211"),
        ("COMPRA DE ACOES", "6211"),
        ("APORTE PLATAFORMA INVESTIMENTO", "6211"),
        ("APLICACAO POUPANCA", "6012"),
        ("TRANSFERENCIA CORRETORA", "6211"),
    ],

    "TRANSPORTE": [
        ("CORRIDA APLICATIVO", "4121"),
        ("PASSAGEM DE ONIBUS", "4111"),
        ("METRO TRANSPORTE", "4111"),
        ("ABASTECIMENTO POSTO", "5541"),
        ("PEDAGIO RODOVIARIO", "4784"),
        ("ESTACIONAMENTO VEICULO", "7523"),
        ("TAXI URBANO", "4121"),
        ("BILHETE TRANSPORTE PUBLICO", "4111"),
    ],

    "COMPRAS_IMPULSO": [
        ("COMPRA LOJA DE ROUPAS", "5651"),
        ("COMPRA ACESSORIOS", "5944"),
        ("COMPRA ONLINE ELETRONICOS", "5732"),
        ("LOJA DE DEPARTAMENTO", "5311"),
        ("COMPRA COSMETICOS", "5977"),
        ("COMPRA DECORACAO", "5712"),
        ("PRESENTE LOJA ONLINE", "5947"),
        ("COMPRA ITEM PROMOCIONAL", "5999"),
    ],

    "SAUDE": [
        ("FARMACIA SAUDE MAIS", "5912"),
        ("CONSULTA MEDICA", "8011"),
        ("CLINICA ODONTOLOGICA", "8021"),
        ("EXAMES LABORATORIAIS", "8071"),
        ("HOSPITAL ATENDIMENTO", "8062"),
        ("COMPRA MEDICAMENTOS", "5912"),
        ("CONSULTA ESPECIALISTA", "8011"),
        ("SERVICO FISIOTERAPIA", "8099"),
    ],
}


# --------------------------------------------------
# FAIXAS DE VALORES
# Valores de saída serão negativos.
# RENDA será positiva.
# --------------------------------------------------

FAIXAS_VALORES = {
    "RENDA": (500, 8000),
    "MORADIA": (80, 2500),
    "ALIMENTACAO": (15, 900),
    "DIVIDA_JUROS": (10, 1800),
    "APOSTAS_BETS": (5, 500),
    "FRAUDE_SUSPEITA": (20, 3000),
    "INVESTIMENTO": (20, 3000),
    "TRANSPORTE": (5, 400),
    "COMPRAS_IMPULSO": (15, 1500),
    "SAUDE": (10, 2000),
}


# --------------------------------------------------
# GERAÇÃO DOS DADOS
# --------------------------------------------------

def gerar_data(rng):
    inicio = datetime(2025, 1, 1)
    fim = datetime(2026, 11, 10)

    intervalo = int((fim - inicio).total_seconds())
    segundos = int(rng.integers(0, intervalo))

    return inicio + timedelta(seconds=segundos)


def gerar_transacao(categoria, indice, rng, aleatorio):
    descricao, mcc = aleatorio.choice(PADROES[categoria])

    minimo, maximo = FAIXAS_VALORES[categoria]
    valor = round(float(rng.uniform(minimo, maximo)), 2)

    # Entradas positivas e saídas negativas.
    if categoria != "RENDA":
        valor = -valor

    # Variação de descrição sem alterar o rótulo.
    variacoes = [
        "",
        " PAGAMENTO",
        " COMPRA",
        " TRANSACAO",
        " ONLINE",
    ]

    descricao += aleatorio.choice(variacoes)

    # Distribui cada categoria entre as 10 personas.
    persona = PERSONAS[indice % len(PERSONAS)]

    # Aposta sempre recebe is_bet=True.
    is_bet = categoria == "APOSTAS_BETS"

    # Score aleatório independente da categoria.
    # Não utilizar como feature do classificador RF02.
    anomaly_score = round(float(rng.uniform(0.01, 0.98)), 2)

    return {
        "transaction_id": f"SYN-{categoria}-{indice + 1:04d}",
        "persona_id": persona,
        "posted_at": gerar_data(rng).isoformat(),
        "amount": valor,
        "payment_method": aleatorio.choice(MEIOS_PAGAMENTO),
        "description_masked": descricao,
        "mcc": str(mcc),
        "category": categoria,
        "is_bet": is_bet,
        "anomaly_score": anomaly_score,
        "ground_truth_note": (
            f"Transacao sintetica criada para representar "
            f"a categoria {categoria}."
        ),
    }


def gerar_dataset():
    rng = np.random.default_rng(SEMENTE)
    aleatorio = random.Random(SEMENTE)

    transacoes = []

    for categoria in CATEGORIAS:
        for indice in range(QUANTIDADE_POR_CATEGORIA):
            transacao = gerar_transacao(
                categoria,
                indice,
                rng,
                aleatorio,
            )
            transacoes.append(transacao)

    return pd.DataFrame(transacoes)


# --------------------------------------------------
# EXECUÇÃO
# --------------------------------------------------

def main():
    print("Gerando transacoes sinteticas...")

    if not ARQUIVO_ORIGINAL.exists():
        raise FileNotFoundError(
            f"Dataset original nao encontrado: {ARQUIVO_ORIGINAL}"
        )

    original = pd.read_csv(
        ARQUIVO_ORIGINAL,
        dtype={"mcc": str},
    )

    novas = gerar_dataset()

    # Verifica se todas as colunas estão presentes.
    if set(original.columns) != set(novas.columns):
        raise ValueError(
            "As colunas do dataset original e do novo dataset "
            "sao diferentes. Verifique o esquema antes de continuar."
        )

    # Mantém a ordem original das colunas.
    novas = novas[original.columns]

    # Junta as 42 originais com as 1.000 novas.
    combinado = pd.concat(
        [original, novas],
        ignore_index=True,
    )

    if combinado["transaction_id"].duplicated().any():
        raise ValueError("Existem IDs de transacao duplicados!")

    # Embaralha os registros.
    combinado = combinado.sample(
        frac=1,
        random_state=SEMENTE,
    ).reset_index(drop=True)

    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combinado.to_csv(
        ARQUIVO_SAIDA,
        index=False,
    )

    print("\nDataset gerado com sucesso!")
    print(f"Arquivo: {ARQUIVO_SAIDA}")
    print(f"Transacoes originais: {len(original)}")
    print(f"Novas transacoes: {len(novas)}")
    print(f"Total: {len(combinado)}")

    print("\nDistribuicao das categorias:")
    print(combinado["category"].value_counts().sort_index())

    print("\nDistribuicao das novas transacoes:")
    print(novas["category"].value_counts().sort_index())


if __name__ == "__main__":
    main()
