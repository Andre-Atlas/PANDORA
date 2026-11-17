"""Pacote do sistema multiagente PANDORA (7 agentes especializados colaborativos)."""

from pandora_rag.agents.graph import GrafoPandora, construir_retriever_padrao
from pandora_rag.agents.models import (
    AnaliseCompulsao,
    DiagnosticoFinanceiro,
    DividaItem,
    EstadoMultiagente,
    EvidenciaNormativa,
    InspecaoFraude,
    MensagemAgente,
    PlanoReestruturacao,
    ResultadoMultiagente,
    VereditoCompliance,
)
from pandora_rag.agents.scenarios import CENARIOS_DEMO, executar_demonstracao
from pandora_rag.agents.specialists import (
    AnalistaAgent,
    CoachAgent,
    ComplianceAgent,
    EducadorAgent,
    EstrategistaAgent,
    GuardiaoAgent,
    OrquestradorAgent,
)

__all__ = [
    "CENARIOS_DEMO",
    "AnaliseCompulsao",
    "AnalistaAgent",
    "CoachAgent",
    "ComplianceAgent",
    "DiagnosticoFinanceiro",
    "DividaItem",
    "EducadorAgent",
    "EstadoMultiagente",
    "EstrategistaAgent",
    "EvidenciaNormativa",
    "GrafoPandora",
    "GuardiaoAgent",
    "InspecaoFraude",
    "MensagemAgente",
    "OrquestradorAgent",
    "PlanoReestruturacao",
    "ResultadoMultiagente",
    "VereditoCompliance",
    "construir_retriever_padrao",
    "executar_demonstracao",
]
