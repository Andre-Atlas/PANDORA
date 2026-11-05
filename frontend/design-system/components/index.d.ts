import * as React from "react";

/** Ícone de traço em grade de 24px, com a cor herdada do texto. */
export interface IconeProps { nome: string; tamanho?: number; traco?: number; rotulo?: string; className?: string }
export function Icone(props: IconeProps): React.ReactElement;

/** Faixa fina de ornamento grego para o registro de leitura. */
export interface FrisoProps { tipo?: "meandro" | "onda" | "palmeta" | "serra" | "ramo"; tom?: "forte" | "vaso" | "base"; curto?: boolean; grande?: boolean }
export function Friso(props: FrisoProps): React.ReactElement;

/** Friso grego que abre todo cabeçalho do mito. */
export interface MeandroProps {  }
export function Meandro(props: MeandroProps): React.ReactElement;

/** Dentes de serra da base do vaso, que encerram o cabeçalho do mito. */
export interface SerraProps {  }
export function Serra(props: SerraProps): React.ReactElement;

/** Marca do produto: a caixa aberta com os espíritos saindo. */
export interface CaixaMarcaProps { tamanho?: number; rotulo?: string }
export function CaixaMarca(props: CaixaMarcaProps): React.ReactElement;

/** Elpis, a assistente: a esperança que ficou na caixa, em medalhão de figura negra. */
export interface ElpisProps { tamanho?: number; estado?: "normal" | "ouvindo"; rotulo?: string }
export function Elpis(props: ElpisProps): React.ReactElement;

/** Brasão de etapa da trilha: emblema em figura negra no medalhão de meandro. */
export interface BrasaoProps { emblema: "templo" | "balanca" | "espiral" | "oliveira" | "elmo" | "anfora"; estado?: "feito" | "atual" | "proximo"; tamanho?: number; rotulo?: string }
export function Brasao(props: BrasaoProps): React.ReactElement;

/** Ânfora que enche conforme a reserva cresce. */
export interface AnforaProps { nivel: number; altura?: number; rotulo?: string }
export function Anfora(props: AnforaProps): React.ReactElement;

/** Botão em pílula com altura mínima de 52px. */
export interface BotaoProps { variante?: "primario" | "secundario" | "fantasma" | "mito" | "claro"; bloco?: boolean; ampliado?: boolean; icone?: string; seta?: boolean; desativado?: boolean; onClick?: () => void; children: React.ReactNode }
export function Botao(props: BotaoProps): React.ReactElement;

/** Botão redondo de 44px só com ícone. */
export interface BotaoIconeProps { icone: string; rotulo: string; tom?: "mito" | "acao"; onClick?: () => void }
export function BotaoIcone(props: BotaoIconeProps): React.ReactElement;

/** Botão grande de microfone, canal principal de quem digita com dificuldade. */
export interface BotaoVozProps { ativo?: boolean; rotulo?: string; onClick?: () => void }
export function BotaoVoz(props: BotaoVozProps): React.ReactElement;

/** Alternância entre duas ou três visões da mesma tela. */
export interface SegmentoProps { opcoes: string[]; valor: string; rotulo: string; onChange?: (v: string) => void }
export function Segmento(props: SegmentoProps): React.ReactElement;

/** Liga e desliga uma trava voluntária. */
export interface AlternadorProps { titulo: string; descricao?: string; ligado?: boolean }
export function Alternador(props: AlternadorProps): React.ReactElement;

/** Barra de progresso de fluxo com voltar e pular. */
export interface ProgressoProps { passo: number; total: number; voltar?: boolean; pular?: boolean }
export function Progresso(props: ProgressoProps): React.ReactElement;

/** Opção em cartão para perguntas de escolha única. */
export interface OpcaoCartaoProps { titulo: string; descricao?: string; icone?: string; marcada?: boolean; onClick?: () => void }
export function OpcaoCartao(props: OpcaoCartaoProps): React.ReactElement;

/** Escala de 1 a 10 sobre como a pessoa se sente com o dinheiro. */
export interface EscalaSentimentoProps { valor?: number }
export function EscalaSentimento(props: EscalaSentimentoProps): React.ReactElement;

/** Caixa de aceite com texto claro, para LGPD. */
export interface ConsentimentoProps { marcado?: boolean; children: React.ReactNode }
export function Consentimento(props: ConsentimentoProps): React.ReactElement;

/** Contêiner do registro de leitura. */
export interface CartaoProps { titulo?: string; sobre?: string; tom?: "apoio" | "alerta" | "ok"; marco?: boolean; className?: string; children?: React.ReactNode }
export function Cartao(props: CartaoProps): React.ReactElement;

/** Etiqueta curta de estado, sempre com ícone e palavra. */
export interface SeloProps { tom?: "neutro" | "ok" | "alerta" | "fonte" | "mito"; icone?: string | null; children: React.ReactNode }
export function Selo(props: SeloProps): React.ReactElement;

/** Marca um número que veio do motor determinístico. */
export interface SeloCalculadoProps {  }
export function SeloCalculado(props: SeloCalculadoProps): React.ReactElement;

/** Barra de proporção com até duas partes. */
export interface TrilhoProps { partes: {valor: number; tom: "acao" | "ok" | "vaso"}[]; total?: number; rotulo: string }
export function Trilho(props: TrilhoProps): React.ReactElement;

/** A única coisa que Elpis notou e vale dizer agora. */
export interface InsightProps { sobre?: string; acao?: string; children: React.ReactNode }
export function Insight(props: InsightProps): React.ReactElement;

/** Atalho em cartão para outra área do app. */
export interface LinkCartaoProps { icone: string; titulo: string; descricao?: string; onClick?: () => void }
export function LinkCartao(props: LinkCartaoProps): React.ReactElement;

/** Uma dívida na ordem do plano. */
export interface LinhaDividaProps { nome: string; valor: string; ordem?: number; protegida?: boolean; children?: React.ReactNode }
export function LinhaDivida(props: LinhaDividaProps): React.ReactElement;

/** Degraus de templo com as etapas do plano. */
export interface DegrausProgressoProps { passos: number; atual: number }
export function DegrausProgresso(props: DegrausProgressoProps): React.ReactElement;

/** Balão de conversa de Elpis ou da pessoa. */
export interface BalaoProps { autor?: "elpis" | "voce"; children: React.ReactNode }
export function Balao(props: BalaoProps): React.ReactElement;

/** Fonte oficial de uma resposta: norma, artigo e link. */
export interface CitacaoCartaoProps { norma: string; href: string; rotuloLink: string; children?: React.ReactNode }
export function CitacaoCartao(props: CitacaoCartaoProps): React.ReactElement;

/** Resultado do motor determinístico dentro da conversa. */
export interface BlocoCalculadoProps { linhas: [string, string][] }
export function BlocoCalculado(props: BlocoCalculadoProps): React.ReactElement;

/** Campo de conversa com anexo e microfone. */
export interface CampoPerguntaProps { placeholder?: string; anexo?: boolean }
export function CampoPergunta(props: CampoPerguntaProps): React.ReactElement;

/** Cabeçalho da conversa com a nota de privacidade. */
export interface CabecalhoElpisProps { nota?: string }
export function CabecalhoElpis(props: CabecalhoElpisProps): React.ReactElement;

/** Caminho com as seis etapas de educação financeira. */
export interface TrilhaCaminhoProps { etapas?: {n: number; t: string; x: number; lado: "d" | "e"; estado: "feito" | "atual" | "proximo"; marco: string | null; emblema: string}[] }
export function TrilhaCaminho(props: TrilhaCaminhoProps): React.ReactElement;

/** Resposta de quiz com retorno que explica. */
export interface QuizOpcaoProps { letra: string; estado?: "neutra" | "certa" | "revisar"; onClick?: () => void; children: React.ReactNode }
export function QuizOpcao(props: QuizOpcaoProps): React.ReactElement;

/** Área rolável com a barra em forma de coluna. */
export interface RolagemProps { rotulo?: string; children?: React.ReactNode }
export function Rolagem(props: RolagemProps): React.ReactElement;

/** Moldura de celular com 390px de tela para mostrar telas. */
export interface AparelhoProps { topo?: "leitura" | "mito" | "base"; altura?: number; children?: React.ReactNode }
export function Aparelho(props: AparelhoProps): React.ReactElement;

/** Cabeçalho do registro do mito, com meandro e serra. */
export interface CabecalhoMitoProps { titulo?: string; subtitulo?: string; voltar?: boolean; acao?: React.ReactNode; children?: React.ReactNode }
export function CabecalhoMito(props: CabecalhoMitoProps): React.ReactElement;

/** Navegação inferior na base preta do vaso, com Elpis ao centro. */
export interface NavBaseProps { ativo?: "inicio" | "dividas" | "elpis" | "trilha" | "guardiao"; onNavegar?: (id: string) => void }
export function NavBase(props: NavBaseProps): React.ReactElement;

/** Mapa completo do app: 7 telas e 2 estados. */
export interface GaleriaProps { ids?: string[] }
export function Galeria(props: GaleriaProps): React.ReactElement;

/** Tela 1: abertura, sentimento, o que pesa e como começar. */
export interface TelaAberturaProps { passo?: 0 | 1 | 2 | 3; cena?: string }
export function TelaAbertura(props: TelaAberturaProps): React.ReactElement;

/** Tela 2: início com o Raio-X do mês. */
export interface TelaInicioProps {  }
export function TelaInicio(props: TelaInicioProps): React.ReactElement;

/** Tela 3: dívidas na ordem do plano e dossiê. */
export interface TelaDividasProps {  }
export function TelaDividas(props: TelaDividasProps): React.ReactElement;

/** Tela 4: assistente RAG com fonte, limites e voz. */
export interface TelaElpisProps { modo?: "citacao" | "limites" | "voz" }
export function TelaElpis(props: TelaElpisProps): React.ReactElement;

/** Tela 5: trilha gamificada de educação financeira e lição. */
export interface TelaTrilhaProps { modo?: "licao"; resposta?: "a" | "b" | "c" | null }
export function TelaTrilha(props: TelaTrilhaProps): React.ReactElement;

/** Tela 6: proteção contra golpes e apostas. */
export interface TelaGuardiaoProps { modo?: "golpes" | "apostas" }
export function TelaGuardiao(props: TelaGuardiaoProps): React.ReactElement;

/** Tela 7: reserva, previsão e simulador. */
export interface TelaMetasProps {  }
export function TelaMetas(props: TelaMetasProps): React.ReactElement;

/** Estado: fluxo de crise. */
export interface TelaCriseProps {  }
export function TelaCrise(props: TelaCriseProps): React.ReactElement;

/** Estado: leitura ampliada com voz. */
export interface TelaGuardiaoAmpliadaProps {  }
export function TelaGuardiaoAmpliada(props: TelaGuardiaoAmpliadaProps): React.ReactElement;

