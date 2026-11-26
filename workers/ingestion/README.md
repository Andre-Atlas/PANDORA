# Ingestão de extratos (#57)

Lê extratos **OFX** (1.x e 2.x) e **CSV** e entrega todos no mesmo esquema de transação
(`src/pandora_ingestion/esquema.py`). Os campos e os valores dos enums são os de `TransacaoLida` na API
(`apps/api/src/pandora_api/dominio/transacao.py`): valor em centavos inteiros (negativo é saída), forma de
pagamento `PIX`, `DEBIT_CARD`, `CREDIT_CARD`, `BOLETO`, `DIRECT_DEBIT` ou `OTHER`, datas com fuso de Brasília.

```bash
cd workers/ingestion
uv run pytest
uv run pandora-ingestion extrato.ofx --saida transacoes.jsonl --nome "NOME DO TITULAR"
```

| Etapa | Onde | O que faz |
|---|---|---|
| Parsers | `ofx.py`, `csv_.py` | OFX por tags (aceita 1.x sem fechamento, cp1252, vírgula decimal); CSV com `;` ou `,`, datas BR ou ISO, coluna de natureza D/C |
| Normalização | `normalizar.py` | datas para America/Sao_Paulo, valor para centavos, sinal, forma de pagamento, parcela, MCC |
| PII | `mascara.py` | CPF, CNPJ, e-mail, telefone, agência e conta, nome de pessoa depois de "PIX ENVIADO", "TED"..., e o nome do titular informado. O `ACCTID` do OFX vira um id opaco |
| Duplicatas | `deduplicar.py` | chave por conta + FITID, ou conta + data + valor + descrição + ordem de ocorrência no arquivo |
| Entrada | `importador.py` | escolhe o parser pela extensão, aplica tudo e grava só o que é novo |

**Logs e erros** têm só contagens, números de linha e motivos. Nunca o conteúdo do arquivo.

**Limites conhecidos**
- Nome de pessoa só é pego depois de expressões típicas de extrato ou quando o titular é informado. Nome solto no meio da descrição passa.
- A máscara pode esconder demais ("PIX ENVIADO ALUGUEL APARTAMENTO" vira "PIX ENVIADO ***"); é o lado seguro.
- Extratos que se sobrepõem e cortam o mesmo dia em pontos diferentes podem contar ocorrências diferentes de transações idênticas.
- PDF é a #66; Open Finance é a #77.
- A API ainda usa o leitor provisório (`adaptadores/ingestao/csv_provisorio.py`). Ligar este pacote a ela é um adaptador de `LeitorExtrato`, a combinar com o Víctor.
