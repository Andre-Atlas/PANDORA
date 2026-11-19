# Pipeline de ingestão

`coletar → extrair → chunking → indexar`, na CLI `pandora-rag`.

1. **Coleta** (`ingest/collect.py`): baixa cada fonte de `fontes.yaml` com HTTP/1.1 (o Planalto recusa HTTP/2), 3 tentativas e pausa de 1 s. Grava o SHA-256 e o tamanho em `corpus.lock`.
2. **Extração** (`ingest/extract.py`): HTML por blocos de texto; PDF com pymupdf, filtrando cabeçalho e rodapé. Remove texto riscado (`<strike>`, `<s>`, `<del>`), que é revogado. Grava em `data/text/{id}.jsonl`, fora do git.
3. **Chunking** (`ingest/chunk.py`): ver [03](03-chunking.md). Ids `fonte#numero`; artigos citados ganham `#c{n}`; partes ganham `-pN`; colisões ganham `~n`.
4. **Indexação** (`pandora-rag indexar`): embedding com cache por conteúdo e carga no pgvector.

Revogações e ressalvas: artigos vetados ou revogados ficam fora. Normas que alteram outra (ex.: trecho inserido na Lei 8.009) registram a norma alterada em `alvo`. A decisão do STF de 23/04/2026 (ADPFs 1005/1006/1097) fica como `ressalva` nos trechos afetados, e aparece na resposta.

Versão do corpus: hash do conjunto de SHA-256 das fontes (`versao_do_corpus`).

## Inventário e coleta do catálogo (issue #54)

As 31 fontes do [catálogo](../evidencias/01-catalogo-fontes-uso-finalidade-e-implementacao.md) estão na seção `catalogo` de `fontes.yaml`. Cada item tem órgão, frequência esperada de mudança e um ou mais **alvos** (arquivo ou endpoint). A tabela pronta está em [10-inventario-fontes.md](10-inventario-fontes.md).

- **Um coletor por tipo** (`coleta/coletores.py`): `html`, `pdf` e `api`. Cada um valida o que baixou (HTML com marca de página, PDF com `%PDF-`, API com JSON válido), então uma página de erro com status 200 vira falha e não entra no bruto.
- **Bruto com data e hash** (`coleta/executor.py`): o arquivo vai para `data/raw/` (`{fonte_id}.{ext}` para alvos do corpus, `catalogo/{alvo}.{ext}` para os demais) e `catalogo.lock.json` guarda `sha256`, `bytes` e `coletado_em`. Só regrava quando o hash muda; rodar de novo sem mudança não cria arquivo nem altera o lock.
- **Cortesia com os servidores**: `robots.txt` por origem (páginas e PDFs; as APIs documentadas ficam de fora), intervalo mínimo de 1 s por origem, 3 tentativas com espera crescente em erro de rede, 429, 304 e 5xx, respeitando `Retry-After`. 404 e outros 4xx não repetem.
- **Falha isolada**: cada alvo é independente. A falha vira `falha` (ou `bloqueada_robots`) no lock, mantendo o último bruto bom, e a execução segue.
- **Tratamento manual**: alvo com `manual: "motivo"` não é baixado e fica registrado como `manual`. O item do catálogo fica `coletada`, `mista`, `manual`, `falha` ou `pendente`.

```bash
uv run pandora-rag coletar-catalogo                  # todos os alvos
uv run pandora-rag coletar-catalogo --alvo sgs-432   # só um
uv run pandora-rag inventario --md ../../docs/rag/10-inventario-fontes.md
```

Os datasets do Hugging Face entram só pelo cartão da API (`/api/datasets/...`), que traz a revisão e a data de modificação; os dados são baixados no treino e na avaliação. A agenda por frequência e o webhook de reprocessamento são a issue #76.
