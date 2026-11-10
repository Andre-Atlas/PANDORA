
import re
import unicodedata

VERSAO = "baseline-0.1.0"


def normalizar(texto: str) -> str:
    texto = str(texto).upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"[^A-Z0-9 ]", " ", texto).strip()


REGRAS = [
    (
        "FRAUDE_SUSPEITA",
        [
            r"GOLPE",
            r"FRAUDE",
            r"PIX SUSPEITO",
            r"COMPRA NAO RECONHECIDA",
            r"CONTA DESCONHECIDA",
            r"FORA PADRAO",
            r"TERCEIROS",
            r"TAXA VIP",
            r"DESCONTO RMC",
            r"CONTA DELEGADA",
            r"PIX ENVIADO PESSOA FISICA.*OUTLET",
        ],
    ),
    (
        "APOSTAS_BETS",
        [r"BET", r"APOSTA", r"BET BR"],
    ),
    (
        "DIVIDA_JUROS",
        [
            r"ROTATIVO",
            r"JUROS",
            r"IOF",
            r"EMPRESTIMO",
            r"FATURA",
            r"CONSIGNADO",
        ],
    ),
    (
        "RENDA",
        [
            r"SALARIO",
            r"REPASSE",
            r"RECEBIMENTO",
            r"BENEFICIO",
            r"VENCIMENTOS",
            r"CREDITO BOLSA",
            r"VERBAS RESCISORIAS",
            r"FGTS",
            r"SEGURO DESEMPREGO",
        ],
    ),
    (
        "MORADIA",
        [
            r"ALUGUEL",
            r"RESIDENCIAL",
            r"CONDOMINIO",
            r"FINANCIAMENTO IMOBILIARIO",
        ],
    ),
    (
        "ALIMENTACAO",
        [r"SUPERMERCADO", r"RESTAURANTE", r"ALIMENTACAO"],
    ),
    (
        "INVESTIMENTO",
        [r"INVESTIMENTO", r"APLICACAO", r"CDB", r"TESOURO"],
    ),
    (
        "TRANSPORTE",
        [r"UBER", r"99APP", r"POSTO", r"COMBUSTIVEL"],
    ),
    (
        "SAUDE",
        [r"FARMACIA", r"HOSPITAL", r"CONSULTA", r"MEDICO"],
    ),
    (
        "COMPRAS_IMPULSO",
        [
            r"SHOPPING",
            r"VESTUARIO",
            r"COMPRA ONLINE",
            r"MARKETPLACE",
            r"FAST FASHION",
            r"LOJA ELETRONICOS",
            r"LOJA ONLINE",
            r"SMARTPHONE",
        ],
    ),
]

        

def classificar_transacao(tx: dict) -> dict:
    descricao = normalizar(tx.get("description_masked", ""))
    mcc = str(tx.get("mcc", "")).zfill(4)

    categoria = "NAO_CLASSIFICADO"
    confianca = 0.0
    evidencia = []

    # MCC 7995 é um forte indício de aposta.
    if mcc == "7995":
        categoria = "APOSTAS_BETS"
        confianca = 0.95
        evidencia.append({"regra": "mcc_7995"})

    else:
        for nome_categoria, padroes in REGRAS:
            encontrados = [
                padrao for padrao in padroes
                if re.search(padrao, descricao)
            ]

            if encontrados:
                categoria = nome_categoria
                confianca = 0.90
                evidencia.append({
                    "regra": "descricao_regex",
                    "termos": encontrados,
                })
                break

    return {
        "transacao_id": tx.get("transaction_id", ""),
        "modelo": "classificador",
        "versao": VERSAO,
        "saida": {"categoria": categoria},
        "confianca": confianca,
        "evidencia": evidencia,
    }
