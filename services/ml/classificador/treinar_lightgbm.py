
from pathlib import Path

import joblib
import pandas as pd

from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from services.ml.classificador.config import (
    CATEGORIAS,
    VERSAO_LIGHTGBM,
    SEMENTE,
)


ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    ROOT
    / "docs/evidencias/datasets/"
    / "transacoes_sinteticas_expandidas.csv"
)

MODEL_PATH = ROOT / "models" / "lightgbm_classifier.joblib"


def carregar_dados():
    df = pd.read_csv(DATASET_PATH, dtype={"mcc": str})

    colunas_obrigatorias = [
        "description_masked",
        "mcc",
        "amount",
        "posted_at",
        "payment_method",
        "category",
    ]

    faltantes = set(colunas_obrigatorias) - set(df.columns)

    if faltantes:
        raise ValueError(f"Colunas ausentes no dataset: {faltantes}")

    df = df.dropna(subset=["category"]).copy()

    categorias_invalidas = set(df["category"]) - set(CATEGORIAS)

    if categorias_invalidas:
        raise ValueError(
            f"Categorias não reconhecidas: {categorias_invalidas}"
        )

    return df


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

    X["amount"] = pd.to_numeric(X["amount"], errors="coerce").fillna(0)

    data = pd.to_datetime(X.pop("posted_at"), errors="coerce")

    X["hora"] = data.dt.hour.fillna(0)
    X["dia_semana"] = data.dt.dayofweek.fillna(0)
    X["mes"] = data.dt.month.fillna(0)

    return X


def criar_pipeline():
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "descricao",
                TfidfVectorizer(
                    max_features=1000,
                    ngram_range=(1, 2),
                ),
                "description_masked",
            ),
            (
                "categoricas",
                OneHotEncoder(handle_unknown="ignore"),
                ["mcc", "payment_method"],
            ),
            (
                "numericas",
                "passthrough",
                ["amount", "hora", "dia_semana", "mes"],
            ),
        ]
    )

    classificador = LGBMClassifier(
        objective="multiclass",
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=7,
        max_depth=-1,
        min_child_samples=1,
        class_weight="balanced",
        random_state=SEMENTE,
        verbosity=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessamento", preprocessor),
            ("classificador", classificador),
        ]
    )


def treinar():
    df = carregar_dados()

    X = preparar_features(df)
    y = df["category"]

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEMENTE,
        stratify=y,
    )

    modelo = criar_pipeline()
    modelo.fit(X_treino, y_treino)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "modelo": modelo,
            "versao": VERSAO_LIGHTGBM,
            "categorias": sorted(y.unique()),
        },
        MODEL_PATH,
    )

    print(f"Modelo salvo em: {MODEL_PATH}")
    print(f"Versão: {VERSAO_LIGHTGBM}")
    print(f"Total de transações: {len(df)}")
    print(f"Transações de treino: {len(X_treino)}")
    print(f"Transações de teste: {len(X_teste)}")
    print(f"Categorias: {sorted(y.unique())}")


if __name__ == "__main__":
    treinar()
