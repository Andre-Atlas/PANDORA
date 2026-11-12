
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from services.ml.classificador.config import CATEGORIAS


ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "lightgbm_classifier.joblib"


def criar_dados_teste():
    dados = [
        # RENDA
        ("CREDITO DE SALARIO EMPRESA XYZ", 3500, "PIX", "RENDA"),
        ("TRANSFERENCIA RECEBIDA DE CLIENTE", 1200, "PIX", "RENDA"),
        ("DEPOSITO DE PAGAMENTO MENSAL", 2800, "BOLETO", "RENDA"),

        # MORADIA
        ("DEBITO AUTOMATICO CONDOMINIO RESIDENCIAL", -650, "DIRECT_DEBIT", "MORADIA"),
        ("PAGAMENTO IMOBILIARIA ALUGUEL", -1500, "PIX", "MORADIA"),
        ("FATURA DE ENERGIA DA RESIDENCIA", -180, "BOLETO", "MORADIA"),

        # ALIMENTACAO
        ("COMPRA MERCADO BOM PRECO", -245, "CREDIT_CARD", "ALIMENTACAO"),
        ("PAGAMENTO RESTAURANTE ALMOCO", -65, "DEBIT_CARD", "ALIMENTACAO"),
        ("COMPRA HORTIFRUTI DA SEMANA", -90, "PIX", "ALIMENTACAO"),

        # DIVIDA_JUROS
        ("COBRANCA DE JUROS DO CREDITO", -120, "DIRECT_DEBIT", "DIVIDA_JUROS"),
        ("AMORTIZACAO DE EMPRESTIMO BANCARIO", -450, "BOLETO", "DIVIDA_JUROS"),
        ("PAGAMENTO DE PARCELA EM ATRASO", -300, "PIX", "DIVIDA_JUROS"),

        # APOSTAS_BETS
        ("TRANSFERENCIA PARA CASA DE PALPITES", -50, "PIX", "APOSTAS_BETS"),
        ("RECARGA DE SALDO PLATAFORMA ESPORTIVA", -100, "CREDIT_CARD", "APOSTAS_BETS"),
        ("DEPOSITO EM SITE DE JOGOS ONLINE", -75, "PIX", "APOSTAS_BETS"),

        # FRAUDE_SUSPEITA
        ("COMPRA NAO RECONHECIDA CARTAO", -890, "CREDIT_CARD", "FRAUDE_SUSPEITA"),
        ("SAQUE SUSPEITO EM TERMINAL DESCONHECIDO", -500, "DEBIT_CARD", "FRAUDE_SUSPEITA"),
        ("TRANSFERENCIA PIX NAO AUTORIZADA", -1300, "PIX", "FRAUDE_SUSPEITA"),

        # INVESTIMENTO
        ("APLICACAO EM RENDA FIXA", -1000, "PIX", "INVESTIMENTO"),
        ("COMPRA DE TITULOS FINANCEIROS", -500, "PIX", "INVESTIMENTO"),
        ("APORTE MENSAL EM CORRETORA", -300, "PIX", "INVESTIMENTO"),

        # TRANSPORTE
        ("RECARGA CARTAO DE ONIBUS", -80, "CREDIT_CARD", "TRANSPORTE"),
        ("CORRIDA APLICATIVO MOBILIDADE", -32, "CREDIT_CARD", "TRANSPORTE"),
        ("ABASTECIMENTO POSTO RODOVIA", -220, "DEBIT_CARD", "TRANSPORTE"),

        # COMPRAS_IMPULSO
        ("COMPRA DE FONE SEM FIO", -350, "CREDIT_CARD", "COMPRAS_IMPULSO"),
        ("PEDIDO DE ACESSORIO POR APLICATIVO", -95, "CREDIT_CARD", "COMPRAS_IMPULSO"),
        ("AQUISICAO DE ITEM DECORATIVO", -140, "PIX", "COMPRAS_IMPULSO"),

        # SAUDE
        ("CONSULTA COM MEDICO ESPECIALISTA", -280, "CREDIT_CARD", "SAUDE"),
        ("EXAME LABORATORIAL PARTICULAR", -190, "PIX", "SAUDE"),
        ("SESSAO DE FISIOTERAPIA", -100, "DEBIT_CARD", "SAUDE"),
    ]

    hoje = pd.Timestamp.now().normalize()

    return pd.DataFrame(
        [
            {
                "description_masked": descricao,
                "mcc": "0000",
                "amount": valor,
                "posted_at": hoje,
                "payment_method": pagamento,
                "category_esperada": categoria,
            }
            for descricao, valor, pagamento, categoria in dados
        ]
    )

def preparar_features(df):
    X = df[
        [
            "description_masked",
            "mcc",
            "amount",
            "posted_at",
            "payment_method",
        ]
    ].copy()

    X["description_masked"] = (
        X["description_masked"].fillna("").astype(str)
    )

    X["mcc"] = X["mcc"].fillna("0000").astype(str).str.zfill(4)

    X["payment_method"] = (
        X["payment_method"].fillna("DESCONHECIDO").astype(str)
    )

    X["amount"] = pd.to_numeric(
        X["amount"], errors="coerce"
    ).fillna(0)

    data = pd.to_datetime(X.pop("posted_at"), errors="coerce")

    X["hora"] = data.dt.hour.fillna(0)
    X["dia_semana"] = data.dt.dayofweek.fillna(0)
    X["mes"] = data.dt.month.fillna(0)

    return X


def avaliar():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado: {MODEL_PATH}"
        )

    artefato = joblib.load(MODEL_PATH)
    modelo = artefato["modelo"]

    df = criar_dados_teste()

    y_real = df["category_esperada"]

    X = preparar_features(
    df.drop(columns=["category_esperada"])
)

    previsoes = modelo.predict(X)

    resultado = df[["description_masked", "category_esperada"]].copy()
    resultado["categoria_prevista"] = previsoes
    resultado["acertou"] = (
        resultado["category_esperada"]
        == resultado["categoria_prevista"]
    )

    print("\n===== RESULTADO POR TRANSAÇÃO =====")
    print(resultado.to_string(index=False))

    print("\n===== RESULTADOS GERAIS =====")
    print(f"Total de transações: {len(df)}")
    print(f"Acertos: {resultado['acertou'].sum()}")
    print(f"Erros: {(~resultado['acertou']).sum()}")
    print(
        f"Acurácia: "
        f"{accuracy_score(y_real, previsoes):.4f}"
    )

    print("\n===== MÉTRICAS POR CATEGORIA =====")
    print(
        classification_report(
            y_real,
            previsoes,
            labels=CATEGORIAS,
            zero_division=0,
        )
    )

    print("\n===== MATRIZ DE CONFUSÃO =====")
    print(
        pd.DataFrame(
            confusion_matrix(
                y_real,
                previsoes,
                labels=CATEGORIAS,
            ),
            index=CATEGORIAS,
            columns=CATEGORIAS,
        )
    )


if __name__ == "__main__":
    avaliar()
