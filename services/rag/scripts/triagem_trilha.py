"""Triagem manual do conteúdo gerado da trilha (`pandora-rag gerar-trilha`).

A validação automática confere citação, número e formato, mas não percebe pergunta ambígua, fora do tema ou
baseada em dado que o STF mandou atualizar. Esta triagem registra, com o motivo, cada pergunta removida e cada
trecho editado. Rode depois de gerar a trilha:

    uv run python scripts/triagem_trilha.py

É idempotente. A revisão humana completa do conteúdo fica para o segundo refino.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pandora_rag.config import REPO_ROOT  # noqa: E402
from pandora_rag.trilha import limpar_marcadores  # noqa: E402

ARQUIVO = REPO_ROOT / "apps" / "api" / "src" / "pandora_api" / "dados" / "trilha.v1.json"

# (lição, trecho do enunciado, motivo)
REMOVER = [
    ("minimo-existencial", "valor mínimo do mínimo existencial estabelecido pelo Decreto",
     "apresenta R$ 303 como valor vigente, mas a decisão do STF (fonte 2) manda o CMN estudar a atualização do valor"),
    ("juros-e-cet", "Qual informação é obrigatória",
     "mais de uma opção é correta: o Art. 54-B exige taxa de juros, CET e valor das prestações"),
    ("golpes-e-med", "notificação de infração no Pix",
     "a opção marcada como certa não responde à pergunta com clareza"),
    ("reserva-de-emergencia", "em caso de separação",
     "foge do tema da reserva de emergência"),
]

# (lição, trecho antigo, texto novo, motivo)
EDITAR = [
    ("minimo-existencial",
     "O mínimo existencial é a renda mensal mínima que deve ser preservada para garantir a subsistência do consumidor "
     "superendividado, equivalente a 25% do salário mínimo vigente na data de publicação do Decreto n. 11.150/2022 [1].",
     "O mínimo existencial é a parcela da renda que deve ser preservada para garantir a subsistência do consumidor "
     "superendividado [1]. O valor dessa parcela é definido por decreto, e o Supremo Tribunal Federal determinou que o "
     "Conselho Monetário Nacional faça estudos técnicos todo ano para avaliar a atualização dele [2].",
     "o texto gerado tratava os 25% do Decreto 11.150/2022 como valor atual; a fonte 2 diz que o STF mandou atualizá-lo"),
]


def _hash(etapas: list[dict]) -> str:
    return hashlib.sha256(json.dumps(etapas, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main(caminho: Path = ARQUIVO) -> int:
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    por_id = {e["licao"]["id"]: e["licao"] for e in doc["etapas"]}
    removidas, editadas, avisos = [], [], []
    ja = doc.get("triagem") or {"removidas": [], "editadas": []}

    for licao in por_id.values():  # antes das edições, para o texto bater com o que elas esperam
        licao["explicacao"] = limpar_marcadores(licao["explicacao"], len(licao["fontes"]))

    for licao_id, trecho, motivo in REMOVER:
        licao = por_id[licao_id]
        antes = len(licao["perguntas"])
        achadas = [p for p in licao["perguntas"] if trecho in p["enunciado"]]
        licao["perguntas"] = [p for p in licao["perguntas"] if trecho not in p["enunciado"]]
        for p in achadas:
            removidas.append({"licao": licao_id, "enunciado": p["enunciado"], "motivo": motivo})
        if len(licao["perguntas"]) == antes and not any(r["licao"] == licao_id and r["motivo"] == motivo for r in ja["removidas"]):
            avisos.append(f"nada a remover em {licao_id}: '{trecho}'")

    for licao_id, antigo, novo, motivo in EDITAR:
        licao = por_id[licao_id]
        if antigo in licao["explicacao"]:
            licao["explicacao"] = licao["explicacao"].replace(antigo, novo)
            editadas.append({"licao": licao_id, "motivo": motivo})
        elif not any(e["licao"] == licao_id and e["motivo"] == motivo for e in ja["editadas"]):
            avisos.append(f"trecho a editar não encontrado em {licao_id}")

    for licao in por_id.values():
        n_fontes = len(licao["fontes"])
        citadas = [int(n) for n in re.findall(r"\[(\d+)\]", licao["explicacao"])]
        licao["citacoes_explicacao"] = sorted({n for n in citadas if 1 <= n <= n_fontes})
        if not licao["perguntas"]:
            avisos.append(f"lição {licao['id']} ficou sem perguntas")

    removidas = ja["removidas"] + [r for r in removidas if r not in ja["removidas"]]  # mantém execuções anteriores
    editadas = ja["editadas"] + [e for e in editadas if e not in ja["editadas"]]
    doc["triagem"] = {
        "nota": "Triagem manual sobre a validação automática. A revisão humana completa fica para o segundo refino.",
        "removidas": removidas,
        "editadas": editadas,
    }
    doc["validacao"] = "automatica+triagem"
    doc["hash"] = _hash(doc["etapas"])
    caminho.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for a in avisos:
        print("AVISO:", a)
    print(f"removidas={len(removidas)} editadas={len(editadas)} hash={doc['hash'][:12]}")
    return 1 if any("ficou sem perguntas" in a for a in avisos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
