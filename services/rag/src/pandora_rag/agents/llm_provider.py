"""Provedor LangChain/LangGraph para Tool Calling nativo com Ollama (qwen2.5:7b) e Anthropic."""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

from pandora_rag.generate.gateway import OLLAMA_URL, carregar_modelos
from pandora_rag.generate.pii import mascarar

logger = logging.getLogger(__name__)

MODELO_PADRAO_AGENTES = "qwen25-7b"


@dataclass
class RegistroToolCall:
    """Registro auditável de uma chamada de ferramenta (@tool) decidida pelo LLM do agente."""

    name: str
    args: dict[str, Any]
    output: Any


@dataclass
class ResultadoAgenteLLM:
    """Resultado completo do ciclo LLM + Tool Calling de um agente especializado."""

    agente: str
    modelo_id: str
    usou_llm: bool
    tool_calls: list[RegistroToolCall] = field(default_factory=list)
    parecer_llm: str = ""
    latencia_s: float = 0.0
    erro_fallback: str | None = None


def resolver_config_modelo(chave_ou_id: str | None) -> dict[str, Any] | None:
    """Resolve uma chave do modelos.yaml (ex.: 'qwen25-7b') ou ID direto do Ollama ('qwen2.5:7b')."""
    if not chave_ou_id or chave_ou_id.strip().lower() in {"offline", "deterministico", "none"}:
        return None
    chave = chave_ou_id.strip()
    cfg = carregar_modelos().get("modelos", {})
    if chave in cfg:
        return dict(cfg[chave])
    # Permite passar o nome direto do modelo no Ollama (ex.: 'qwen2.5:7b')
    for info in cfg.values():
        if info.get("id") == chave:
            return dict(info)
    return {"provedor": "ollama", "id": chave, "externo": False}


def ollama_disponivel(timeout: float = 1.5) -> bool:
    """Verifica rapidamente se o daemon local do Ollama responde em OLLAMA_URL."""
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def construir_chat_model(
    chave_ou_id: str | None = MODELO_PADRAO_AGENTES,
    max_tokens: int = 512,
) -> tuple[BaseChatModel | None, str]:
    """Instancia ChatOllama ou ChatAnthropic com suporte nativo a bind_tools."""
    info = resolver_config_modelo(chave_ou_id)
    if info is None:
        return None, "offline"

    modelo_id = str(info["id"])
    provedor = info.get("provedor", "ollama")

    if provedor == "ollama":
        from langchain_ollama import ChatOllama

        chat = ChatOllama(
            model=modelo_id,
            base_url=OLLAMA_URL,
            temperature=0,
            num_predict=max_tokens,
            num_ctx=8192,
        )
        return chat, modelo_id

    if provedor == "anthropic":
        from langchain_anthropic import ChatAnthropic

        chat = ChatAnthropic(
            model_name=modelo_id,
            max_tokens_to_sample=max_tokens,
            timeout=120.0,
            max_retries=2,
        )
        return chat, modelo_id

    raise ValueError(f"Provedor de LLM não suportado: {provedor}")


def _serializar_saida_tool(valor: Any) -> str:
    if hasattr(valor, "model_dump"):
        return json.dumps(valor.model_dump(), ensure_ascii=False)
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False, default=str)
    return str(valor)


def executar_agente_com_tools(
    *,
    agente: str,
    chat_model: BaseChatModel | None,
    modelo_id: str,
    system_prompt: str,
    user_prompt: str,
    tools: list[BaseTool],
    sintetizar_apos_tool: bool = False,
) -> ResultadoAgenteLLM:
    """Executa um agente no padrão LangChain Tool Calling (bind_tools -> tool_calls -> execução).

    - Aplica máscara de PII (RNF01) em system_prompt e user_prompt antes de enviar ao modelo.
    - Vincula as @tools via chat_model.bind_tools(tools).
    - Executa as tools solicitadas pelo LLM em ai_msg.tool_calls.
    - Opcionalmente faz a segunda passagem (ToolMessage -> AIMessage) quando sintetizar_apos_tool=True.
    """
    if chat_model is None:
        return ResultadoAgenteLLM(
            agente=agente,
            modelo_id="offline",
            usou_llm=False,
        )

    sys_limpo, _ = mascarar(system_prompt)
    usr_limpo, _ = mascarar(user_prompt)
    mapa_tools: dict[str, BaseTool] = {t.name: t for t in tools}

    t0 = time.perf_counter()
    registros: list[RegistroToolCall] = []

    try:
        mensagens: list[Any] = [
            SystemMessage(content=sys_limpo),
            HumanMessage(content=usr_limpo),
        ]
        llm_vinculado = chat_model.bind_tools(tools) if tools else chat_model
        ai_msg = llm_vinculado.invoke(mensagens)

        tool_calls = getattr(ai_msg, "tool_calls", None) or []
        mensagens.append(ai_msg)

        for tc in tool_calls:
            nome_tool = tc.get("name", "")
            args_tool = dict(tc.get("args") or {})
            call_id = tc.get("id") or f"call_{nome_tool}"
            tool_obj = mapa_tools.get(nome_tool)
            if tool_obj is None:
                continue
            saida = tool_obj.invoke(args_tool)
            registros.append(RegistroToolCall(name=nome_tool, args=args_tool, output=saida))
            mensagens.append(
                ToolMessage(
                    content=_serializar_saida_tool(saida),
                    tool_call_id=call_id,
                    name=nome_tool,
                )
            )

        texto_final = ""
        if isinstance(ai_msg, AIMessage) and isinstance(ai_msg.content, str):
            texto_final = ai_msg.content.strip()

        if sintetizar_apos_tool and registros and not texto_final:
            ai_pos = chat_model.invoke(mensagens)
            if isinstance(ai_pos, AIMessage) and isinstance(ai_pos.content, str):
                texto_final = ai_pos.content.strip()

        parecer_seguro, _ = mascarar(texto_final)
        return ResultadoAgenteLLM(
            agente=agente,
            modelo_id=modelo_id,
            usou_llm=True,
            tool_calls=registros,
            parecer_llm=parecer_seguro,
            latencia_s=round(time.perf_counter() - t0, 4),
        )
    except Exception as exc:  # noqa: BLE001 - resiliência fail-safe para não abortar o grafo
        logger.warning("Agente '%s' encontrou erro no LLM (%s); acionando fallback de tool: %s", agente, modelo_id, exc)
        return ResultadoAgenteLLM(
            agente=agente,
            modelo_id=modelo_id,
            usou_llm=False,
            tool_calls=registros,
            latencia_s=round(time.perf_counter() - t0, 4),
            erro_fallback=str(exc),
        )
