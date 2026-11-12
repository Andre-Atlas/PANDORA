# PANDORA · API

FastAPI em arquitetura hexagonal (RNF06). Front, ingestão, modelos e agentes conversam por aqui. Issue de origem: #62.

## Como rodar

**Com Docker (um comando).** Na raiz do repositório:

```bash
docker compose up
```

A API fica em http://localhost:8000. O contrato completo fica em http://localhost:8000/docs. O banco é um Postgres com pgvector na porta 5434; a 5433 é do banco do RAG (`services/rag`).

**Sem Docker.** Precisa de [uv](https://docs.astral.sh/uv/) e de um Postgres:

```bash
cd apps/api
uv sync
cp .env.example .env   # ajuste PANDORA_DB_URL
uv run --env-file .env uvicorn pandora_api.principal:app --reload
```

## Testes

```bash
uv run pytest                 # usa repositórios em memória
uv run ruff check src tests
```

O teste do Postgres só roda com um banco de verdade:

```bash
docker compose up -d db
PANDORA_TEST_DB_URL=postgresql://pandora:pandora_local@localhost:5434/pandora uv run pytest tests/test_postgres.py
```

## Arquitetura

```
src/pandora_api/
  dominio/       tipos e regras puras: usuário, sessão, consentimento, transação
  portas/        interfaces: repositórios, hasher de senha, relógio
  aplicacao/     casos de uso: contas, consentimentos, privacidade
  adaptadores/
    http/        FastAPI: rotas, esquemas (o contrato) e erros
    persistencia/  Postgres (psycopg) e memória (testes)
    seguranca/   scrypt e relógio do sistema
  principal.py   monta tudo para o uvicorn
```

`dominio`, `portas` e `aplicacao` não importam FastAPI, Pydantic nem banco. O teste `test_arquitetura.py` garante isso.

## Contrato

O contrato fica em `openapi.json`, que é gerado a partir do código. Depois de mudar uma rota ou um esquema:

```bash
uv run python -m pandora_api.exportar_openapi   # em apps/api
npm run api:tipos -w @pandora/web               # na raiz: gera os tipos do front
```

Se um dos dois arquivos ficar desatualizado, um teste falha: `test_contrato.py` na API, `lib/api/esquema.test.ts` no front.

### Convenções

- **Valores** em centavos inteiros (`valor_centavos`). Nunca `float` para dinheiro (RNF03).
- **Taxas** (`cet_anual`) em decimal, enviadas como texto no JSON para não perder precisão.
- **Datas** em ISO 8601 e UTC.
- **Erros** em `application/problem+json` (RFC 9457), com `type` no formato `urn:pandora:erro:<código>`.
- **Cálculos** do motor determinístico vêm com um bloco `calculo` (fonte e valores usados). O front mostra o selo "Calculado" só quando esse bloco existe.
- **Autenticação**: `POST /auth/sessoes` devolve um token opaco. Envie `Authorization: Bearer <token>`. O banco guarda só o hash do token, e as senhas usam scrypt.

### O que já funciona e o que é de outra issue

| Área | Rotas | Situação |
|---|---|---|
| Sistema | `GET /saude` | Pronta |
| Conta | `POST /auth/cadastro`, `POST /auth/sessoes`, `DELETE /auth/sessoes/atual`, `GET /eu` | Pronta |
| Privacidade | `POST/GET /consentimentos`, `POST /consentimentos/{id}/revogacao`, `DELETE /eu/dados` | Pronta |
| Raio-X | `POST /extratos`, `GET /extratos/{id}`, `GET /transacoes`, `PATCH /transacoes/{id}/categoria`, `GET /raio-x` | Contrato pronto, 501 → #72. O envio já exige consentimento. |
| Dívidas | `GET /dividas`, `GET /score` | Contrato pronto, 501 → #72 (motor da #65) |
| Plano | `POST /plano` | Contrato pronto, 501 → #71 (motor da #65) |
| Previsão | `GET /previsao` | Contrato pronto, 501 → #84 |
| Chat | `POST /chat` | Pronta (#85). **Pública, sem Bearer.** Chama o serviço do RAG (`PANDORA_RAG_URL`); sinal de crise responde com mensagem fixa de apoio e `crise=true`, sem chamar o modelo. 503 se o RAG estiver fora. |
| Trilha | `GET /trilha`, `GET /trilha/licoes/{id}`, `POST /trilha/licoes/{id}/porque` | Pronta. **Pública, sem Bearer.** Conteúdo pré-gerado e triado (`dados/trilha.v1.json`); o "por quê?" é respondido ao vivo pelo RAG. |

As rotas que respondem 501 já validam a sessão e a entrada, e a resposta diz qual issue vai implementá-las. Nenhuma delas devolve dado inventado.

### Exclusão total (RNF01)

`DELETE /eu/dados` apaga a conta, as sessões e os consentimentos. Todo repositório com dado pessoal implementa `apagar_do_usuario` e entra na lista de `Privacidade` em `adaptadores/http/conteiner.py`. Quem criar um repositório novo (transações, extratos, conversas) precisa colocá-lo nessa lista.

### Elpis e Trilha (públicas por enquanto)

`/chat` e `/trilha*` não exigem token: o app ainda não tem login e nada pessoal é guardado (o progresso da trilha fica no navegador). Isso muda o contrato original da #85, que previa sessão. Antes do deploy (#88) é preciso colocar limite de requisições, porque cada pergunta custa de 8 a 14 s de GPU.

O RAG roda como serviço próprio na máquina (MPS e Ollama não existem no container): `uv run pandora-rag servir` em `services/rag`, porta 8010. A API lê `PANDORA_RAG_URL` (padrão `http://localhost:8010`).

## Pendências

- **Esquema de transação em rascunho.** Os campos seguem o dataset sintético da #51 (`services/ml/sintetico`, na branch `dev/rayssa`). Falta fechar com a ingestão da Luana (#57), que é o passo 3 da #62. Os nomes estão em português (`valor_centavos`, `descricao_mascarada`); o dataset usa inglês (`amount`, `description_masked`).
- **Chat sem streaming.** O RAG de hoje devolve a resposta inteira. Se o chat passar a usar streaming, o contrato de `POST /chat` muda.
- **Sem limite de tentativas de login.** Bom acrescentar antes do deploy (#88).
