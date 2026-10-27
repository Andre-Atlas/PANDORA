# ADR-0002 · Dados bancários via agregador em sandbox + upload

**Status:** Aceito · **Data:** 2026-10-27

## Contexto
O valor do PANDORA depende de ler a movimentação real do usuário. Para receber dados no Open Finance Brasil é preciso ser uma instituição participante autorizada pelo Banco Central, o que um projeto acadêmico não é. Usar dados reais de pessoas também traria um risco de LGPD desproporcional.

## Decisão
1. Integrar um **agregador** (Pluggy como primeira opção, Belvo como alternativa) em **modo sandbox/trial**, por trás de uma porta `BankDataPort`.
2. Oferecer **upload de OFX/CSV/PDF** e **foto de boleto/fatura** como caminho que funciona sem conexão bancária.
3. Desenvolver e avaliar com **dados sintéticos** gerados a partir das personas.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Integração direta com Open Finance | Exige autorização do BCB |
| Scraping de internet banking | Viola termos de uso, é frágil e inseguro |
| Só dados sintéticos | Não demonstra o fluxo real de conexão |

## Consequências
- A demo é realista sem dado real.
- Trocar de agregador é só trocar o adapter.
- Um produto real exigiria contrato comercial com o agregador e revisão jurídica do consentimento.
