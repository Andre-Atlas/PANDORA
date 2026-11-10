/**
 * Nomes curtos para os tipos do contrato da API.
 *
 * `esquema.d.ts` é gerado de `apps/api/openapi.json`. Não edite à mão:
 *   uv run python -m pandora_api.exportar_openapi   (em apps/api)
 *   npm run api:tipos -w @pandora/web
 */
import type { components, operations, paths } from "./esquema";

type Esquemas = components["schemas"];

export type { components, operations, paths };

export type Problema = Esquemas["Problema"];
export type Usuario = Esquemas["UsuarioSaida"];
export type Sessao = Esquemas["SessaoSaida"];
export type Consentimento = Esquemas["ConsentimentoSaida"];
export type Finalidade = Esquemas["Finalidade"];
export type Calculo = Esquemas["Calculo"];

/** Rascunho: segue o dataset sintético da #51; falta fechar com a ingestão (#57). */
export type Transacao = Esquemas["TransacaoSaida"];
export type Categoria = Esquemas["Categoria"];
export type PaginaTransacoes = Esquemas["PaginaTransacoes"];
export type RaioX = Esquemas["RaioX"];
export type Extrato = Esquemas["ExtratoSaida"];

export type Divida = Esquemas["DividaSaida"];
export type Score = Esquemas["Score"];
export type Plano = Esquemas["Plano"];
export type MetodoPlano = Esquemas["MetodoPlano"];
export type Previsao = Esquemas["Previsao"];

export type RespostaChat = Esquemas["RespostaChat"];
export type Citacao = Esquemas["CitacaoSaida"];
