import joblib
import pandas as pd
from services.ml.classificador.treinar_lightgbm import preparar_features, MODEL_PATH

dados = joblib.load(MODEL_PATH)
modelo = dados["modelo"]

transacoes = pd.DataFrame([
    {
        "description_masked": "SUPERMERCADO",
        "mcc": "5411",
        "amount": 250.00,
        "posted_at": "2026-11-10 12:30:00",
        "payment_method": "CREDITO",
    },
    {
        "description_masked": "PAGAMENTO ALUGUEL",
        "mcc": "6513",
        "amount": 1200.00,
        "posted_at": "2026-11-10 10:00:00",
        "payment_method": "PIX",
    },
])

X = preparar_features(transacoes)
predicoes = modelo.predict(X)
probabilidades = modelo.predict_proba(X)

for i, categoria in enumerate(predicoes):
    confianca = probabilidades[i].max()
    print(f"Transação {i + 1}: {categoria}")
    print(f"Confiança: {confianca:.2%}")