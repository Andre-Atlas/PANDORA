# Arquitetura

```mermaid
flowchart LR
    subgraph Ingestão
        F[fontes.yaml] --> C[coleta: HTTP + SHA-256]
        C --> X[extração: HTML/PDF → texto]
        X --> K[chunking estrutural]
    end
    K --> E[embedding bge-m3]
    K --> B[índice BM25]
    E --> P[(pgvector HNSW)]
    Q[pergunta] --> V[busca vetorial top-50]
    Q --> BQ[busca BM25 top-50]
    P --> V
    B --> BQ
    V --> R[RRF]
    BQ --> R
    R --> RR[reranker bge-reranker-v2-m3 top-30]
    RR --> G{portão de abstenção<br/>nota ≥ 0,02?}
    G -- não --> A[mensagem de abstenção]
    G -- sim --> L[LLM local qwen2.5:14b, top-3]
    L --> S[resposta com [n] + fontes]
```

- **Ingestão** ([02](02-pipeline-ingestao.md)): 33 fontes oficiais versionadas em `services/rag/corpus.lock`.
- **Índice**: vetores e BM25 saem dos mesmos chunks; o Postgres guarda os registros, e o BM25 é reconstruído a cada versão do corpus.
- **Fusão**: RRF com `k=60`, pesos iguais.
- **Portão**: se a nota do melhor chunk no reranker for menor que 0,02, o LLM nem é chamado.
- **Gateway** (`pandora_rag/generate/gateway.py`): interface única para Ollama e Anthropic, com máscara de PII (CPF, CNPJ, telefone, e-mail, cartão) antes de chamada externa e teto de US$ 30. Nesta versão só há modelos locais.
