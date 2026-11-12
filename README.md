# PANDORA

> Challenge 2 · CBL · Big Idea **Qualidade de Vida**: *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*
> Tema do grupo: **Finanças**.

## Essential Question

> **Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?**

## O problema em números

| Indicador | Valor | Fonte |
|---|---|---|
| Brasileiros inadimplentes | **81,7 milhões** (fev/2026) | [Serasa](https://www.serasa.com.br/imprensa/10-anos-do-mapa-de-inadimplencia/) |
| Famílias endividadas | **81,7%** (set/2026) | [CNC/Peic](https://portaldocomercio.org.br/acoes-institucionais/cnc-inadimplencia-e-endividamento-das-familias-brasileiras-recuam-em-setembro/) |
| Juros do rotativo do cartão | **435,9% a.a.** (fev/2026) | [Agência Brasil / BCB](https://agenciabrasil.ebc.com.br/economia/noticia/2026-03/juros-do-cartao-de-credito-pesam-mais-para-familias-em-fevereiro) |
| Pix para apostas online | **R$ 20,8 bilhões** em ago/2024 | [BCB, Estudo Especial 119/2024](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf) |
| Vítimas de golpes com Pix ou boleto | **24 milhões**, quase R$ 29 bi (jul/2024–jun/2025) | [Datafolha/FBSP](https://www12.senado.leg.br/radio/1/noticia/2025/08/18/mais-de-24-milhoes-de-pessoas-foram-vitimas-de-golpes-pelo-pix) |

## Telas

Protótipo gerado pelo [design system](frontend/design-system/README.md): 7 telas e 2 estados, em 16 quadros.

### Versões das interfaces

| Versão | O que mudou | Onde ver |
|---|---|---|
| **3 · Responsiva** (10/11/2026, [#106](https://github.com/Andre-Atlas/PANDORA/pull/106)) | Layout para celular, tablet e desktop, em retrato e paisagem. Meandro no lugar da serra, navbar retrátil, mito em figura negra no tema claro e em figura vermelha no escuro, abertura com a cena esfumada. | [Figma: telas em 6 tamanhos e 2 temas](https://www.figma.com/design/g19U79NnQEMfGIXxPwgdDe) · [Prévia interativa](https://claude.ai/artifact/CrTqPZbKTiQSULhxNSWJLW) · [Design system](https://claude.ai/artifact/PiHQsMY79M1frKVo9tcNDX) · [capturas](frontend/design-system/assets/Telas/responsivo) |
| **2 · Ornamentos gregos** (05/11/2026, [#100](https://github.com/Andre-Atlas/PANDORA/pull/100) e [#101](https://github.com/Andre-Atlas/PANDORA/pull/101)) | Optima e Cinzel Decorative, ornamentos nos componentes, brasões na trilha. Só celular. | A grade abaixo · [código desta versão](https://github.com/Andre-Atlas/PANDORA/tree/a6b3970/frontend/design-system) |
| **1 · Identidade visual** (05/11/2026, [#2](https://github.com/Andre-Atlas/PANDORA/pull/2) e [#3](https://github.com/Andre-Atlas/PANDORA/pull/3)) | Primeira versão: tokens, componentes e galeria de 16 quadros. | [Telas desta versão](https://github.com/Andre-Atlas/PANDORA/tree/7219288/frontend/design-system/assets/Telas) · [código desta versão](https://github.com/Andre-Atlas/PANDORA/tree/7219288/frontend/design-system) |

Para ver a versão atual no navegador, abra [`frontend/design-system/index.html`](frontend/design-system/index.html) (a galeria completa), ou rode `node frontend/design-system/src/teste.js --saida <pasta>` e abra `tela.html` e `responsivo.html` dessa pasta. A Prévia interativa e o Design system ficam no claude.ai e só abrem para quem recebeu acesso.

<table>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/inicio-celular-claro.jpg" alt="Início no celular, tema claro" width="150"><br><sub>Início · celular · claro</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/inicio-celular-escuro.jpg" alt="Início no celular, tema escuro" width="150"><br><sub>Início · celular · escuro</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/navbar-recolhida-celular.jpg" alt="Início no celular com a navbar recolhida" width="150"><br><sub>Navbar recolhida · celular</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/abertura-celular.jpg" alt="Abertura no celular" width="150"><br><sub>Abertura · celular</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/inicio-desktop-claro.jpg" alt="Início no desktop, tema claro, com o trilho lateral" width="320"><br><sub>Início · desktop · claro</sub></td>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/abertura-desktop.jpg" alt="Abertura no desktop com a cena esfumada" width="320"><br><sub>Abertura · desktop</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/dividas-tablet-escuro.jpg" alt="Dívidas no tablet deitado, tema escuro" width="320"><br><sub>Dívidas · tablet deitado · escuro</sub></td>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/navbar-recolhida-desktop-escuro.jpg" alt="Início no desktop, tema escuro, com o trilho recolhido" width="320"><br><sub>Navbar recolhida · desktop · escuro</sub></td>
  </tr>
</table>

Versão 2, só celular:

<table>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-01.png" alt="1a · Abertura" width="200"><br><sub>1a · Abertura</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-02.png" alt="1b · Como se sente" width="200"><br><sub>1b · Como se sente</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-03.png" alt="1c · O que pesa" width="200"><br><sub>1c · O que pesa</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-04.png" alt="1d · Como começar" width="200"><br><sub>1d · Como começar</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-05.png" alt="2 · Início (Raio-X)" width="200"><br><sub>2 · Início (Raio-X)</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-06.png" alt="3 · Dívidas" width="200"><br><sub>3 · Dívidas</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-07.png" alt="4a · Elpis: resposta com fonte" width="200"><br><sub>4a · Elpis: resposta com fonte</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-08.png" alt="4b · Elpis: limites" width="200"><br><sub>4b · Elpis: limites</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-09.png" alt="4c · Elpis: voz" width="200"><br><sub>4c · Elpis: voz</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-10.png" alt="5a · Trilha" width="200"><br><sub>5a · Trilha</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-11.png" alt="5b · Trilha: lição" width="200"><br><sub>5b · Trilha: lição</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-12.png" alt="6a · Guardião: golpes" width="200"><br><sub>6a · Guardião: golpes</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-13.png" alt="6b · Guardião: apostas" width="200"><br><sub>6b · Guardião: apostas</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-14.png" alt="7 · Metas e previsão" width="200"><br><sub>7 · Metas e previsão</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-15.png" alt="E1 · Fluxo de crise" width="200"><br><sub>E1 · Fluxo de crise</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-16.png" alt="E2 · Leitura ampliada" width="200"><br><sub>E2 · Leitura ampliada</sub></td>
  </tr>
</table>

## Identidade visual

<table>
  <tr>
    <td align="center"><img src="frontend/design-system/assets/Cena/pandora-cena-1600.webp" alt="Cena da abertura" width="200"><br><sub>Cena da abertura</sub></td>
    <td align="center"><img src="frontend/design-system/assets/Marca/caixa-esperanca.svg" alt="Marca: caixa da esperança" width="120"><br><sub>Marca: caixa da esperança</sub></td>
    <td align="center"><img src="frontend/design-system/assets/Marca/elpis-medalhao.svg" alt="Medalhão de Elpis" width="120"><br><sub>Medalhão de Elpis</sub></td>
  </tr>
</table>

<img src="frontend/design-system/assets/Ornamentos/meandro.svg" alt="Ornamento meandro" width="480">

<img src="frontend/design-system/assets/Ornamentos/serra.svg" alt="Ornamento serra" width="480">

## Documentação

| Documento | Conteúdo |
|---|---|
| [Problema e Essential Question](docs/01-problema-e-essential-question.md) | Contexto, stakeholders, personas e fontes |
| [Escopo e Concepção (MD + PDF)](docs/escopo/README.md) | Cenário, 10 Guiding Questions, 6 Stakeholders, 5 Personas, RF/RNF (4 Graus), Riscos, Premissas, Métricas e [PDF (5 páginas)](docs/escopo/PANDORA-Documento-de-Escopo-CBL.pdf) |
| [Personas e Jornadas](docs/personas/README.md) | 5 personas exclusivas (fichas individuais, dores, casos de uso e barreiras) |
| [Evidências](docs/evidencias/README.md) | Visão geral do acervo |
| [Notícias](docs/evidencias/noticias/README.md) | Levantamentos e reportagens 2024–2026 |
| [Artigos](docs/evidencias/artigos/README.md) | Estudos, escalas de bem-estar financeiro e marcos legais |
| [Datasets](docs/evidencias/datasets/README.md) | Séries do BCB, bases públicas e amostra sintética |
