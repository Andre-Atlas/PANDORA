
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)

from services.ml.classificador.config import (
    CATEGORIAS,
    SEMENTE,
)

from services.ml.classificador.treinar_lightgbm import (
    carregar_dados,
    preparar_features,
    MODEL_PATH,
)


CATEGORIAS_ESSENCIAIS = [
    "MORADIA",
    "ALIMENTACAO",
    "SAUDE",
]


def avaliar():
    # Recupera os dados
    df = carregar_dados()

    X = preparar_features(df)
    y = df["category"]

    # Reproduz a mesma divisão usada no treinamento
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEMENTE,
        stratify=y,
    )

    # Carrega o modelo treinado
    artefato = joblib.load(MODEL_PATH)
    modelo = artefato["modelo"]

    # Faz previsões somente nos dados de teste
    previsoes = modelo.predict(X_teste)

    # Métricas gerais
    macro_f1 = f1_score(
        y_teste,
        previsoes,
        average="macro",
        zero_division=0,
    )

    print("\n===== RESULTADOS GERAIS =====")
    print(f"Macro F1: {macro_f1:.4f}")

    print("\n===== MÉTRICAS POR CATEGORIA =====")
    print(
        classification_report(
            y_teste,
            previsoes,
            labels=CATEGORIAS,
            zero_division=0,
        )
    )

    # Avaliação do Mínimo Existencial
    verdadeiro_essencial = y_teste.isin(CATEGORIAS_ESSENCIAIS)
    previsto_essencial = pd.Series(
        previsoes,
        index=y_teste.index,
    ).isin(CATEGORIAS_ESSENCIAIS)

    recall_essencial = recall_score(
        verdadeiro_essencial,
        previsto_essencial,
        pos_label=True,
        zero_division=0,
    )

    print("===== MÍNIMO EXISTENCIAL =====")
    print(f"Recall: {recall_essencial:.4f}")

    # Matriz de confusão
    matriz = confusion_matrix(
        y_teste,
        previsoes,
        labels=CATEGORIAS,
    )

    matriz_df = pd.DataFrame(
        matriz,
        index=CATEGORIAS,
        columns=CATEGORIAS,
    )

    print("\n===== MATRIZ DE CONFUSÃO =====")
    print(matriz_df)


if __name__ == "__main__":
    avaliar()
