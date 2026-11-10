# Pipeline de ingestão

`coletar → extrair → chunking → indexar`, na CLI `pandora-rag`.

1. **Coleta** (`ingest/collect.py`): baixa cada fonte de `fontes.yaml` com HTTP/1.1 (o Planalto recusa HTTP/2), 3 tentativas e pausa de 1 s. Grava o SHA-256 e o tamanho em `corpus.lock`.
2. **Extração** (`ingest/extract.py`): HTML por blocos de texto; PDF com pymupdf, filtrando cabeçalho e rodapé. Remove texto riscado (`<strike>`, `<s>`, `<del>`), que é revogado. Grava em `data/text/{id}.jsonl`, fora do git.
3. **Chunking** (`ingest/chunk.py`): ver [03](03-chunking.md). Ids `fonte#numero`; artigos citados ganham `#c{n}`; partes ganham `-pN`; colisões ganham `~n`.
4. **Indexação** (`pandora-rag indexar`): embedding com cache por conteúdo e carga no pgvector.

Revogações e ressalvas: artigos vetados ou revogados ficam fora. Normas que alteram outra (ex.: trecho inserido na Lei 8.009) registram a norma alterada em `alvo`. A decisão do STF de 23/04/2026 (ADPFs 1005/1006/1097) fica como `ressalva` nos trechos afetados, e aparece na resposta.

Versão do corpus: hash do conjunto de SHA-256 das fontes (`versao_do_corpus`).
