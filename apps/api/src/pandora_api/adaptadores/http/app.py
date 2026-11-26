from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pandora_api import __version__
from pandora_api.adaptadores.http.conteiner import Conteiner
from pandora_api.adaptadores.http.problemas import registrar_tratadores
from pandora_api.adaptadores.http.rotas import chat, conta, contrato, privacidade, raio_x, sistema, trilha

DESCRICAO = """
API do PANDORA. Front, ingestão, modelos e agentes conversam por aqui.

- **Valores** em centavos inteiros. **Taxas** em decimal, enviadas como texto para não perder precisão.
- **Erros** em `application/problem+json`.
- Recursos que ainda não existem respondem **501** com a issue que vai implementá-los.
- **Sem token** (o app ainda não tem login): `/chat` e `/trilha*`. Não guardam dado pessoal.
- **Autenticação**: `POST /auth/sessoes` devolve um token; envie `Authorization: Bearer <token>`.
- **Transação**: esquema em **rascunho** (dataset da #51), a fechar com a ingestão (#57).
- **Extrato**: por enquanto só CSV, com leitor e classificador provisórios (#57 e #68 trazem os de verdade).
"""

TAGS = [
    {"name": "sistema"},
    {"name": "conta", "description": "Cadastro e sessão."},
    {"name": "privacidade", "description": "Consentimento e exclusão total (LGPD)."},
    {"name": "raio-x", "description": "Extratos, transações e Raio-X (#72)."},
    {"name": "dividas", "description": "Mapa de dívidas, score e plano (#65, #71, #72)."},
    {"name": "previsao", "description": "Previsão de caixa (#84)."},
    {"name": "chat", "description": "Elpis, com RAG (#85). Pública: o app ainda não tem login."},
    {"name": "trilha", "description": "Trilha de educação financeira, com fontes. Pública."},
]


def criar_app(conteiner: Conteiner, origens_cors: tuple[str, ...] = (), lifespan=None) -> FastAPI:
    app = FastAPI(
        title="PANDORA API",
        version=__version__,
        description=DESCRICAO,
        openapi_tags=TAGS,
        lifespan=lifespan,
        # operationId = nome da função: vira o nome da operação nos tipos do front.
        generate_unique_id_function=lambda rota: rota.name,
    )
    app.state.conteiner = conteiner
    if origens_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(origens_cors),
            allow_methods=["*"],
            allow_headers=["Authorization", "Content-Type"],
        )
    registrar_tratadores(app)
    app.include_router(sistema.router)
    app.include_router(conta.router)
    app.include_router(privacidade.router)
    for router in (raio_x.router, contrato.dividas, contrato.previsao, chat.router, trilha.router):
        app.include_router(router)
    return app
