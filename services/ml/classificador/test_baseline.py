
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from baseline import classificar_transacao

df = pd.read_csv(
    "docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv",
    dtype={"mcc": str},
)

df["previsto"] = [
    classificar_transacao(tx)["saida"]["categoria"]
    for tx in df.to_dict(orient="records")
]

print("\nRELATÓRIO DE CLASSIFICAÇÃO\n")

print(classification_report(
    df["category"],
    df["previsto"],
    zero_division=0
))

print("\nMATRIZ DE CONFUSÃO\n")

categorias = sorted(set(df["category"]) | set(df["previsto"]))

print(pd.DataFrame(
    confusion_matrix(
        df["category"],
        df["previsto"],
        labels=categorias
    ),
    index=categorias,
    columns=categorias
))

print("\nTRANSAÇÕES CLASSIFICADAS INCORRETAMENTE\n")

erros = df[df["category"] != df["previsto"]]

for _, tx in erros.iterrows():
    print(
        f"ID: {tx['transaction_id']}\n"
        f"Descrição: {tx['description_masked']}\n"
        f"Esperado: {tx['category']}\n"
        f"Previsto: {tx['previsto']}\n"
        f"{'-' * 40}"
    )
