"""Premissas e catálogos do gerador sintético PANDORA (issue #51).

Tudo aqui é dado de entrada do gerador: personas, comerciantes fictícios, taxas e
regras de essencialidade. Nada daqui é dado real. A lógica fica em gerar_dataset.py.
"""
from __future__ import annotations

SEED = 42
FIM_JANELA = (2026, 10)          # a janela de 12 meses termina em out/2026 (mês do CSV de amostra)
MESES_AQUECIMENTO = 3            # meses simulados antes da janela, para parcelas e faturas em curso
FATOR_VOLUME = 1.4               # as sugestões de N somam 11.400; x1,4 atinge o piso de 15.000
PISO_TOTAL = 15_000
PISO_CLASSE_CONSUMO = 300

TAXA_ROTATIVO_MES = 0.150        # 435,9% a.a. (README do repo) => ~15,0% a.m.
IOF_ROTATIVO = 0.004             # aproximação; premissa a validar com a Calculadora do Cidadão
TAXA_CHEQUE_ESPECIAL_MES = 0.079  # 7,9% a.m. (ficha da persona 07; SGS 25463)

RUIDO_FN = 0.08                  # fração dos positivos com rótulo observado trocado para 0
RUIDO_FP_LOOKALIKE = 0.08        # fração dos negativos difíceis com rótulo observado trocado para 1
HOLDOUT = ("antonio_67", "rosangela_43")
SPLIT_ALVO = (0.70, 0.15, 0.15)
MESES_TESTE_PREVISOR = 3

CATEGORIAS_CONSUMO = ["MORADIA", "UTILIDADES", "ALIMENTACAO", "SAUDE", "TRANSPORTE",
                      "EDUCACAO", "LAZER", "COMPRAS_IMPULSO", "INSUMO_MEI"]
CATEGORIAS_CONTEXTO = ["RENDA", "DIVIDA_JUROS", "INVESTIMENTO", "TRANSFERENCIA",
                       "APOSTAS_BETS", "FRAUDE_SUSPEITA"]

# Volumes sugeridos (12 meses, antes do fator). O gerador calibra a taxa de eventos variáveis
# para chegar perto deste alvo.
# Sugestao de N por persona (12 meses, antes do fator). Soma 11.400; x FATOR_VOLUME = 15.960.
# O gerador limita cada persona pela capacidade (orcamento variavel / TICKET_MEDIO_MIN) e redistribui o excedente
# as personas com folga, para manter o piso total sem tickets de centavos (ver README).
N_BASE = {"carla_34": 800, "julia_31": 800, "rafael_39": 800, "mariana_28": 2500,
          "diego_24": 1500, "rosangela_43": 1500, "antonio_67": 600, "lucas_19": 1200,
          "patricia_53": 1000, "fernanda_46": 700}
TICKET_MEDIO_MIN = 8.0           # R$ por evento variavel (media), para o gasto variavel nao virar centavos

PILOTO_PERSONAS = ["carla_34", "diego_24", "antonio_67", "mariana_28", "julia_31"]


# --------------------------------------------------------------------------- catálogo
def C(cat, nomes, mcc, pm, med, sigma=0.55, hora="dia", cnpj=True, parc=0.0):
    return dict(cat=cat, nomes=nomes, mcc=mcc if isinstance(mcc, list) else [mcc], pm=pm,
                med=med, sigma=sigma, hora=hora, cnpj=cnpj, parc=parc)


CATALOGO = {
    "mercado": C("ALIMENTACAO", ["MERCADO BOM PRECO", "SUPERMERCADO CENTRAL", "ATACADO ECONOMICO",
                                 "HIPERMERCADO MAIS", "MERCEARIA DO ZE", "MINIMERCADO ESQUINA"],
                 ["5411", "5422"], {"DEBIT_CARD": .45, "PIX": .20, "CREDIT_CARD": .35}, 85, .7),
    "padaria": C("ALIMENTACAO", ["PADARIA PAO QUENTE", "PANIFICADORA SABOR", "CONFEITARIA DOCE VIDA"],
                 "5462", {"DEBIT_CARD": .5, "PIX": .4, "CREDIT_CARD": .1}, 15, .5, "manha"),
    "feira": C("ALIMENTACAO", ["FEIRA LIVRE BARRACA 12", "HORTIFRUTI VERDE", "SACOLAO DA VILA"],
               "5499", {"PIX": .7, "DEBIT_CARD": .3}, 38, .5, "manha"),
    "restaurante": C("ALIMENTACAO", ["RESTAURANTE SABOR CASEIRO", "CHURRASCARIA FOGO LENTO", "PIZZARIA FORNO LENHA"],
                     "5812", {"DEBIT_CARD": .4, "CREDIT_CARD": .4, "PIX": .2}, 52, .6, "refeicao"),
    "delivery": C("ALIMENTACAO", ["APP DELIVERY PEDIDO", "ENTREGA RAPIDA REFEICAO", "LANCHES EXPRESS"],
                  "5814", {"CREDIT_CARD": .55, "PIX": .30, "DEBIT_CARD": .15}, 44, .5, "refeicao"),
    "refeicao_trabalho": C("ALIMENTACAO", ["LANCHONETE DO PLANTAO", "MARMITARIA ESTRADA", "PADARIA 24H", "LANCHONETE POSTO"],
                           "5814", {"PIX": .5, "DEBIT_CARD": .5}, 24, .4, "refeicao"),
    "farmacia": C("SAUDE", ["FARMACIA POPULAR VIDA", "DROGARIA SAUDE TOTAL", "FARMACIA BEM ESTAR"],
                  "5912", {"DEBIT_CARD": .45, "PIX": .25, "CREDIT_CARD": .30}, 58, .8),
    "consulta": C("SAUDE", ["CLINICA SAUDE INTEGRAL", "LABORATORIO ANALISES", "CONSULTORIO MEDICO ASSOCIADO"],
                  ["8011", "8071"], {"PIX": .5, "CREDIT_CARD": .4, "DEBIT_CARD": .1}, 170, .6),
    "estetica": C("SAUDE", ["STUDIO BELEZA E CIA", "CLINICA ESTETICA LUZ", "BARBEARIA DO CENTRO"],
                  "7230", {"PIX": .5, "DEBIT_CARD": .3, "CREDIT_CARD": .2}, 95, .5),
    "combustivel": C("TRANSPORTE", ["POSTO ESTRADA REAL", "AUTO POSTO CENTRAL", "POSTO RODOVIA NORTE"],
                     "5541", {"DEBIT_CARD": .5, "PIX": .3, "CREDIT_CARD": .2}, 72, .45),
    "bilhete_transporte": C("TRANSPORTE", ["RECARGA BILHETE UNICO", "CARTAO TRANSPORTE URBANO", "RECARGA TRANSPORTE METROPOLITANO"],
                            "4111", {"PIX": .7, "DEBIT_CARD": .3}, 40, .4, "manha"),
    "app_transporte": C("TRANSPORTE", ["APP TRANSPORTE CORRIDA", "APP MOBILIDADE URBANA", "TAXI APP VIAGEM"],
                        "4121", {"CREDIT_CARD": .4, "PIX": .35, "DEBIT_CARD": .25}, 24, .6, "noite"),
    "manutencao_veiculo": C("TRANSPORTE", ["OFICINA MECANICA RODAS", "AUTO PECAS ECONOMICA", "BORRACHARIA 24H"],
                            "7538", {"PIX": .4, "DEBIT_CARD": .3, "CREDIT_CARD": .3}, 190, .8),
    "pedagio_estacionamento": C("TRANSPORTE", ["ESTACIONAMENTO CENTRO", "PEDAGIO AUTOPISTA"],
                                ["7523", "4784"], {"DEBIT_CARD": .5, "PIX": .5}, 17, .4),
    "gas": C("UTILIDADES", ["DEPOSITO GAS E AGUA", "REVENDA GAS ESQUINA"], "5984",
             {"PIX": .7, "DEBIT_CARD": .3}, 115, .15),
    "celular_recarga": C("UTILIDADES", ["RECARGA CELULAR PREPAGO", "OPERADORA MOVEL RECARGA"], "4814",
                         {"PIX": .8, "DEBIT_CARD": .2}, 22, .4),
    "material_escolar": C("EDUCACAO", ["PAPELARIA ESCOLAR", "LIVRARIA UNIVERSITARIA", "COPIAS E MATERIAIS"],
                          "5943", {"DEBIT_CARD": .4, "PIX": .3, "CREDIT_CARD": .3}, 62, .6),
    "curso_online": C("EDUCACAO", ["PLATAFORMA CURSOS ONLINE", "ACADEMIA DIGITAL CURSOS"], "8299",
                      {"CREDIT_CARD": .8, "PIX": .2}, 95, .5, "qualquer"),
    "cinema_show": C("LAZER", ["CINEMA SHOPPING", "INGRESSOS SHOWS ONLINE", "TEATRO MUNICIPAL"],
                     ["7832", "7922"], {"CREDIT_CARD": .5, "PIX": .3, "DEBIT_CARD": .2}, 58, .5, "noite"),
    "bar": C("LAZER", ["BAR DO PORTO", "BOTECO DA PRACA", "CHOPERIA CENTRAL"], "5813",
             {"DEBIT_CARD": .4, "PIX": .35, "CREDIT_CARD": .25}, 62, .7, "noite"),
    "jogos_eletronicos": C("LAZER", ["LOJA GAMES ELETRONICOS", "STORE JOGOS DIGITAIS", "CONSOLE E JOGOS LTDA"],
                           ["5734", "5816", "5945"], {"CREDIT_CARD": .5, "PIX": .4, "DEBIT_CARD": .1}, 130, .8, "noite", parc=.2),
    "passeio": C("LAZER", ["PARQUE DIVERSOES", "PASSEIO TURISTICO LOCAL"], "7996",
                 {"PIX": .5, "DEBIT_CARD": .3, "CREDIT_CARD": .2}, 70, .5),
    "viagem": C("LAZER", ["AGENCIA VIAGENS HORIZONTE", "COMPANHIA AEREA CEU", "HOTEL POUSADA MAR"],
                ["4722", "4511", "7011"], {"CREDIT_CARD": .6, "PIX": .4}, 900, .35, "qualquer", parc=.5),
    "marketplace": C("COMPRAS_IMPULSO", ["MARKETPLACE OFERTAS", "LOJA VIRTUAL SUPER PROMO", "SHOP ONLINE DESCONTOS"],
                     ["5311", "5999"], {"CREDIT_CARD": .75, "PIX": .20, "DEBIT_CARD": .05}, 140, .8, "qualquer", parc=.55),
    "eletronicos_online": C("COMPRAS_IMPULSO", ["LOJA ELETRONICOS ONLINE", "TECNOLOGIA E CIA ONLINE", "CELULARES E ACESSORIOS"],
                            "5732", {"CREDIT_CARD": .8, "PIX": .15, "DEBIT_CARD": .05}, 260, .8, "qualquer", parc=.7),
    "moda": C("COMPRAS_IMPULSO", ["MARKETPLACE FAST FASHION", "LOJA ROUPAS MODA JA", "BRECHO ONLINE"],
              "5651", {"CREDIT_CARD": .7, "PIX": .2, "DEBIT_CARD": .1}, 125, .7, "qualquer", parc=.5),
    # MEI: software_trabalho e software_pessoal compartilham MCC 5734 e parte dos nomes (ambiguidade proposital).
    "software_trabalho": C("INSUMO_MEI", ["LOJA SOFTWARE DIGITAL", "LICENCAS CRIATIVAS ONLINE", "FONTES E TEMPLATES DESIGN"],
                           "5734", {"CREDIT_CARD": .85, "PIX": .15}, 125, .5),
    "material_design": C("INSUMO_MEI", ["BANCO DE IMAGENS PREMIUM", "PAPELARIA CRIATIVA ATELIE", "SUPRIMENTOS DESIGN PRINT"],
                         ["5111", "5943"], {"CREDIT_CARD": .6, "PIX": .4}, 88, .5),
    "impressao": C("INSUMO_MEI", ["GRAFICA RAPIDA IMPRESSOES", "COPIADORA E PLOTAGEM"], "7332",
                   {"PIX": .6, "DEBIT_CARD": .4}, 48, .5),
    "software_pessoal": C("LAZER", ["LOJA SOFTWARE DIGITAL", "APPS E JOGOS ASSINATURA", "STORE APLICATIVOS"],
                          "5734", {"CREDIT_CARD": .9, "PIX": .1}, 58, .6, "noite"),
    "pix_familia": C("TRANSFERENCIA", ["CONTATO"], "4829", {"PIX": 1.0}, 80, .6, "qualquer", cnpj=False),
    "pix_amigo": C("TRANSFERENCIA", ["CONTATO"], "4829", {"PIX": 1.0}, 45, .7, "qualquer", cnpj=False),
    "reparo": C("MORADIA", ["CASA MATERIAIS CONSTRUCAO", "LOJA FERRAGENS E TINTAS", "ELETRICISTA ASSOCIADOS"],
                "5200", {"PIX": .4, "DEBIT_CARD": .35, "CREDIT_CARD": .25}, 150, .8),
    "utensilios_casa": C("MORADIA", ["CASA E UTILIDADES DOMESTICAS", "LOJA ELETRODOMESTICOS LAR", "MAGAZINE COLCHOES E MOVEIS"],
                         ["5712", "5719", "5722"], {"CREDIT_CARD": .35, "PIX": .30, "DEBIT_CARD": .35}, 95, .8, "dia", parc=.25),
    "loterica_conta": C("UTILIDADES", ["CASA LOTERICA SORTE GRANDE", "LOTERICA CENTRAL", "LOTERICA DA ESQUINA"],
                        ["7995", "6012"], {"PIX": .65, "BOLETO": .35}, 95, .4),
}

# Negativos difíceis de aposta: nomes com 'BET' que não são apostas (nome, subtipo do catálogo).
NOMES_CONFUSOS_BET = [("CONFECCOES BETANIA", "moda"), ("BETEL PAPELARIA", "material_escolar"),
                      ("OFICINA DO BETO", "manutencao_veiculo"), ("SALAO ELIZABETE ESTETICA", "estetica"),
                      ("BETONEIRA E MATERIAIS", "reparo")]

HN_PADRAO = dict(loterica=.30, games=.20, nome_bet=.30, viagem=.10, servico_novo=.25, pix_novo=.35)

# --------------------------------------------------------------------------- apostas
# Marcas fictícias (nenhuma é operadora real). As autorizadas vão para lista_spa_sintetica.csv;
# a lista real da SPA/MF (#59) substitui esse arquivo no pipeline de produção.
OPERADORAS_AUTORIZADAS = ["BETX", "BETZOLA", "LUCKYNOVA", "SORTEMAX", "APOSTA10", "GIROFORTE", "ARENABETS", "CRASHPIX"]
OPERADORAS_NAO_AUTORIZADAS = ["REDBETPLUS", "GANHAFACIL", "JOGAMAIS777", "PIXSORTE"]
INTERMEDIADORES = ["PAGAMENTOS RAPIDOS", "PAYFAST INTERMEDIACAO", "INTERMEDIADORA JOGOS ONLINE", "CARTEIRA DIGITAL XPAY"]
MCC_BET_OPERADORA = ["7995", "7995", "7995", "7801", "7802"]
MCC_BET_INTERMEDIADOR = ["6012", "4829", "6051", "7399", "5999"]


# --------------------------------------------------------------------------- personas
def F(cat, sub, desc, dia, valor, pm="PIX", mcc="0000", h=(6, 10), jit=0.0, desde=None, ate=None,
      mes=None, trab=False, dest=None, cnpj=True, instr="conta"):
    return dict(cat=cat, sub=sub, desc=desc, dia=dia, valor=valor, pm=pm, mcc=mcc, h=h, jit=jit,
                desde=desde, ate=ate, mes=mes, trab=trab, dest=dest or f"EMP:{desc}", cnpj=cnpj, instr=instr)


def R(tipo, **kw):
    return dict(tipo=tipo, **kw)


PERSONAS = {
    "carla_34": dict(
        nome="Carla", idade=34, arquetipo="superendividamento_clt", regime="CLT", escolaridade=3, score=340,
        vuln=.85, renda_ref=2850, saldo_ini=300, saldo_alvo=150, cheque_limite=300, p_total=.15, p_mora=.35,
        var_frac=.24, cartao_share=.35, contas=["CARLA_CC_A"], cartoes={"CARLA_CARTAO_1": (2500, 1800)},
        renda=[R("fixa", dia=7, valor=2850, desc="CREDITO SALARIO EMPRESA *** LTDA", pm="PIX", h=(8, 11))],
        fixos=[F("MORADIA", "aluguel", "PAGAMENTO ALUGUEL RESIDENCIAL", 6, 950, "PIX", "6513", dest="PF:senhorio_carla", cnpj=False),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 95, "BOLETO", "4900", jit=.15, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 14, 70, "BOLETO", "4900", jit=.10, dest="CONC:agua"),
               F("UTILIDADES", "celular", "RECARGA PLANO CELULAR", 5, 35, "PIX", "4814", dest="CONC:celular"),
               F("DIVIDA_JUROS", "emprestimo_parcela", "PARCELA EMPRESTIMO PESSOAL BANCO A", 15, 480, "DIRECT_DEBIT", "6012", dest="BANCO:A"),
               F("LAZER", "streaming", "ASSINATURA STREAMING VIDEO", 18, 22.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING1", instr="cartao")],
        pesos=dict(utensilios_casa=.04, reparo=.02, mercado=.34, padaria=.12, feira=.04, farmacia=.10, bilhete_transporte=.12, material_escolar=.02, restaurante=.03, app_transporte=.03, marketplace=.05, pix_familia=.05, pix_amigo=.02, cinema_show=.01, gas=.04, celular_recarga=.02),
        trab_subs=set(), noturno_p={}, bets=None,
        fraude=dict(eps_ano=7.0, tipos=dict(boleto_falso=.5, falso_emprestimo=.3, loja_falsa=.2)),
        impulso=dict(taxa=.6, parc_p=.4), hn={}),
    "diego_24": dict(
        nome="Diego", idade=24, arquetipo="gig_economy_apostador", regime="App/Autonomo", escolaridade=3, score=420,
        vuln=.80, renda_ref=4850, saldo_ini=200, saldo_alvo=100, cheque_limite=300, p_total=.7, p_mora=.15,
        var_frac=.30, cartao_share=.10, contas=["DIEGO_CC_DIGITAL"], cartoes={"DIEGO_CARTAO_1": (800, 0)},
        renda=[R("semanal", wd=2, valor=1120, cv=.10, desc="REPASSE SEMANAL PLATAFORMA ENTREGA", pm="PIX", hm=(9, 10), jm=20)],
        fixos=[F("MORADIA", "contribuicao_casa", "PIX ENVIADO CONTRIBUICAO CASA FAMILIA", 10, 250, "PIX", "4829", dest="PF:familia_diego", cnpj=False),
               F("DIVIDA_JUROS", "financiamento_veiculo", "PARCELA FINANCIAMENTO MOTO", 10, 450, "DIRECT_DEBIT", "6012", dest="BANCO:MOTO"),
               F("UTILIDADES", "celular", "PLANO DADOS CELULAR", 8, 55, "PIX", "4814", dest="CONC:celular")],
        pesos=dict(utensilios_casa=.02, combustivel=.30, manutencao_veiculo=.08, refeicao_trabalho=.16, mercado=.06, delivery=.05, farmacia=.03, jogos_eletronicos=.03, bar=.04, marketplace=.05, pix_familia=.06, pix_amigo=.06, pedagio_estacionamento=.03, padaria=.04, cinema_show=.01),
        trab_subs={"combustivel", "manutencao_veiculo", "pedagio_estacionamento"},
        noturno_p=dict(refeicao_trabalho=.25, combustivel=.18, delivery=.2),
        bets=dict(tipo="compulsivo", sessoes_noite=5.5, bets_por_sessao=(2, 5), stake_med=38, escalada=.20,
                  apos_repasse_p=.80, premio_p=.09, aut=.70, nao_aut=.15, interm=.15, via_filho=False),
        fraude=dict(eps_ano=4.0, tipos=dict(loja_falsa=.5, cartao_clonado=.5)),
        impulso=dict(taxa=.8, parc_p=.2), hn=dict(games=.3)),
    "antonio_67": dict(
        nome="Antonio", idade=67, arquetipo="aposentado_vulneravel", regime="INSS", escolaridade=2, score=560,
        vuln=.95, renda_ref=2412, saldo_ini=900, saldo_alvo=500, cheque_limite=500, p_total=.9, p_mora=.10,
        var_frac=.45, cartao_share=0.0, contas=["ANTONIO_CC_A"], cartoes={},
        renda=[R("fixa", dia=2, valor=2412, desc="BENEFICIO PREVIDENCIARIO INSS", pm="DIRECT_DEBIT", h=(7, 8), dest="INSS")],
        fixos=[F("DIVIDA_JUROS", "consignado", "CONSIGNADO INSS CONTRATO 04", 2, 723.6, "DIRECT_DEBIT", "6012", h=(7, 8), dest="BANCO:CONSIGNADO"),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 10, 110, "BOLETO", "4900", jit=.12, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 12, 65, "BOLETO", "4900", jit=.08, dest="CONC:agua"),
               F("UTILIDADES", "celular", "RECARGA PLANO CELULAR", 6, 40, "PIX", "4814", dest="CONC:celular"),
               F("UTILIDADES", "tv_assinatura", "TV POR ASSINATURA", 15, 89, "DIRECT_DEBIT", "4899", dest="EMP:TV"),
               F("MORADIA", "iptu", "IPTU PARCELA IMOVEL PROPRIO", 20, 380, "BOLETO", "9311", mes=1, dest="PREF:iptu")],
        pesos=dict(utensilios_casa=.03, mercado=.30, padaria=.14, feira=.06, farmacia=.22, consulta=.04, pix_familia=.04, gas=.04, celular_recarga=.02, reparo=.03, restaurante=.04, passeio=.02),
        trab_subs=set(), noturno_p={}, bets=None,
        fraude=dict(eps_ano=12.0, tipos=dict(boleto_falso=.30, falsa_central=.35, falso_emprestimo=.20, desconto_indevido=.15)),
        impulso=dict(taxa=.15, parc_p=0), hn=dict(viagem=.02, games=.02)),
    "mariana_28": dict(
        nome="Mariana", idade=28, arquetipo="mei_volatil_impulso", regime="MEI", escolaridade=5, score=450,
        vuln=.75, renda_ref=4300, saldo_ini=700, saldo_alvo=700, cheque_limite=800, p_total=.70, p_mora=.20,
        var_frac=.22, cartao_share=.45, parc_mult=1.3,
        contas=["MARIANA_BANCO_A_CC", "MARIANA_BANCO_B_CC", "MARIANA_BANCO_C_CC", "MARIANA_BANCO_D_CC"],
        cartoes={"MARIANA_CARTAO_1": (1000, 500), "MARIANA_CARTAO_2": (1200, 600),
                 "MARIANA_CARTAO_3": (800, 300), "MARIANA_CARTAO_4": (600, 300)},
        renda=[R("mei", mu=4300, sd=1000, lo=3200, hi=5800, desc="RECEBIMENTO PROJETO DESIGN MEI CLIENTE")],
        fixos=[F("MORADIA", "aluguel", "PAGAMENTO ALUGUEL APARTAMENTO COMPARTILHADO", 5, 1150, "PIX", "6513", dest="PF:senhorio_mariana", cnpj=False),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 60, "BOLETO", "4900", jit=.15, dest="CONC:energia"),
               F("UTILIDADES", "internet", "INTERNET FIBRA", 15, 110, "DIRECT_DEBIT", "4899", dest="CONC:internet"),
               F("UTILIDADES", "celular", "PLANO CELULAR", 8, 60, "PIX", "4814", dest="CONC:celular"),
               F("INSUMO_MEI", "das_mei", "DAS MEI GUIA MENSAL", 20, 75.9, "BOLETO", "9311", trab=True, dest="RFB:das"),
               F("INSUMO_MEI", "software_trabalho", "LICENCA SOFTWARE DESIGN ASSINATURA", 3, 148, "CREDIT_CARD", "5734", trab=True, dest="EMP:LICENCA_DESIGN", instr="cartao"),
               F("LAZER", "streaming", "ASSINATURA STREAMING VIDEO", 18, 39.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING1", instr="cartao")],
        pesos=dict(utensilios_casa=.04, material_escolar=.02, mercado=.14, restaurante=.07, delivery=.09, marketplace=.12, moda=.08, eletronicos_online=.06, bar=.05, cinema_show=.03, material_design=.13, impressao=.08, software_trabalho=.08, software_pessoal=.03, app_transporte=.05, farmacia=.04, consulta=.02, pix_amigo=.04, padaria=.03, curso_online=.02),
        trab_subs={"software_trabalho", "material_design", "impressao", "das_mei"},
        noturno_p=dict(delivery=.15, software_pessoal=.3), bets=dict(tipo="casual", sessoes_noite=.25, bets_por_sessao=(1, 3), stake_med=25, escalada=.1,
                                                                  apos_repasse_p=0, premio_p=.1, aut=.8, nao_aut=.1, interm=.1, via_filho=False),
        fraude=dict(eps_ano=8.0, tipos=dict(loja_falsa=.5, cartao_clonado=.5)),
        impulso=dict(taxa=1.4, parc_p=.65), rolagem=.5, hn=dict(viagem=.10, games=.3)),
    "julia_31": dict(
        nome="Julia", idade=31, arquetipo="pos_divida_clt", regime="CLT", escolaridade=5, score=640,
        vuln=.25, renda_ref=4500, saldo_ini=1500, saldo_alvo=1500, cheque_limite=1500, p_total=.95, p_mora=.03,
        var_frac=.32, cartao_share=.50, contas=["JULIA_CC_A"], cartoes={"JULIA_CARTAO_1": (3000, 350)},
        renda=[R("fixa", dia=5, valor=4500, desc="CREDITO SALARIO CLT EMPRESA TECH", pm="PIX", h=(8, 9))],
        fixos=[F("MORADIA", "aluguel", "PAGAMENTO ALUGUEL APARTAMENTO", 6, 1100, "PIX", "6513", dest="PF:senhorio_julia", cnpj=False),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 90, "BOLETO", "4900", jit=.12, dest="CONC:energia"),
               F("UTILIDADES", "internet", "INTERNET FIBRA", 15, 100, "DIRECT_DEBIT", "4899", dest="CONC:internet"),
               F("UTILIDADES", "celular", "PLANO CELULAR", 8, 50, "PIX", "4814", dest="CONC:celular"),
               F("LAZER", "streaming", "ASSINATURA STREAMING VIDEO", 18, 39.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING1", instr="cartao"),
               F("LAZER", "streaming", "ASSINATURA STREAMING MUSICA", 20, 21.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING2", instr="cartao"),
               F("DIVIDA_JUROS", "acordo_divida", "PARCELA ACORDO DIVIDA RENEGOCIADA", 12, 400, "DIRECT_DEBIT", "6012", ate=(2026, 7), dest="BANCO:ACORDO"),
               F("INVESTIMENTO", "aplicacao", "APLICACAO TESOURO SELIC RESERVA EMERGENCIA", 5, 120, "DIRECT_DEBIT", "6211", h=(10, 10), ate=(2026, 7), dest="CORR:TESOURO"),
               F("INVESTIMENTO", "aplicacao", "APLICACAO TESOURO SELIC RESERVA EMERGENCIA", 5, 500, "DIRECT_DEBIT", "6211", h=(10, 10), desde=(2026, 8), dest="CORR:TESOURO")],
        pesos=dict(utensilios_casa=.04, material_escolar=.02, mercado=.22, padaria=.06, restaurante=.08, delivery=.05, farmacia=.05, consulta=.03, app_transporte=.06, bilhete_transporte=.05, cinema_show=.04, bar=.05, curso_online=.05, marketplace=.05, moda=.05, pix_familia=.04, pix_amigo=.03, estetica=.03, passeio=.03),
        trab_subs=set(), noturno_p={}, bets=None,
        fraude=dict(eps_ano=5.0, tipos=dict(loja_falsa=.4, golpe_investimento=.6)),
        impulso=dict(taxa=.4, parc_p=.3), hn=dict(viagem=.25)),
    "rosangela_43": dict(
        nome="Rosangela", idade=43, arquetipo="beneficiaria_social_bets_familia", regime="Diarista+Bolsa Familia", escolaridade=1, score=280,
        vuln=.90, renda_ref=1560, saldo_ini=80, saldo_alvo=80, cheque_limite=100, p_total=.9, p_mora=.45,
        var_frac=.22, cartao_share=0.0, contas=["ROSANGELA_CC_A"], cartoes={},
        renda=[R("fixa", dia=17, valor=700, desc="CREDITO BENEFICIO BOLSA FAMILIA", pm="PIX", h=(6, 7), dest="GOV:BOLSA"),
               R("diarias", lam=9, med=95, sd=20, desc="RECEBIMENTO PIX DIARIA CLIENTE ***")],
        fixos=[F("MORADIA", "aluguel", "PAGAMENTO ALUGUEL CASA", 8, 350, "PIX", "6513", dest="PF:senhorio_rosangela", cnpj=False),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 10, 105, "BOLETO", "4900", jit=.2, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 14, 80, "BOLETO", "4900", jit=.1, dest="CONC:agua"),
               F("DIVIDA_JUROS", "agiota", "PIX ENVIADO PESSOA FISICA ***", 20, 100, "PIX", "4829", dest="PF:agiota_rosangela", cnpj=False)],
        pesos=dict(utensilios_casa=.03, material_escolar=.04, mercado=.42, padaria=.12, feira=.06, farmacia=.06, bilhete_transporte=.14, pix_familia=.05, gas=.03, celular_recarga=.05, restaurante=.01, reparo=.02),
        trab_subs=set(), noturno_p={},
        bets=dict(tipo="filho", sessoes_noite=4.0, bets_por_sessao=(1, 4), stake_med=30, escalada=.2, apos_repasse_p=.85,
                  premio_p=.06, aut=.55, nao_aut=.30, interm=.15, via_filho=True),
        fraude=dict(eps_ano=6.0, tipos=dict(golpe_pix_beneficio=.5, loja_falsa=.3, falso_emprestimo=.2)),
        impulso=dict(taxa=.1, parc_p=0), hn=dict(viagem=.01, games=.05, loterica=.45)),
    "rafael_39": dict(
        nome="Rafael", idade=39, arquetipo="servidor_cheque_especial", regime="Servidor", escolaridade=5, score=520,
        vuln=.50, renda_ref=7000, saldo_ini=-1500, saldo_alvo=-1800, cheque_limite=3000, p_total=.90, p_mora=.08,
        var_frac=.10, cartao_share=.45, contas=["RAFAEL_CC_A", "RAFAEL_CC_B"], cartoes={"RAFAEL_CARTAO_1": (5000, 1500)},
        renda=[R("fixa", dia=10, valor=5200, desc="CREDITO SALARIO SERVIDOR ESTADO", pm="DIRECT_DEBIT", h=(6, 7), dest="ESTADO"),
               R("conjuge", valor=900, desc="PIX RECEBIDO CONJUGE")],
        fixos=[F("MORADIA", "aluguel", "PAGAMENTO ALUGUEL CASA", 12, 1300, "PIX", "6513", dest="PF:senhorio_rafael", cnpj=False),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 180, "BOLETO", "4900", jit=.12, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 14, 90, "BOLETO", "4900", jit=.1, dest="CONC:agua"),
               F("UTILIDADES", "internet", "INTERNET FIBRA", 15, 130, "DIRECT_DEBIT", "4899", dest="CONC:internet"),
               F("UTILIDADES", "celular", "PLANO CELULAR FAMILIA", 8, 90, "DIRECT_DEBIT", "4814", dest="CONC:celular"),
               F("SAUDE", "plano_saude", "MENSALIDADE PLANO DE SAUDE FAMILIA", 12, 420, "DIRECT_DEBIT", "6300", dest="EMP:PLANO_SAUDE"),
               F("EDUCACAO", "mensalidade", "MENSALIDADE ESCOLA INFANTIL", 5, 650, "BOLETO", "8211", dest="EMP:ESCOLA_INFANTIL"),
               F("DIVIDA_JUROS", "consignado", "CONSIGNADO FOLHA CONTRATO 02", 10, 640, "DIRECT_DEBIT", "6012", dest="BANCO:CONSIGNADO"),
               F("DIVIDA_JUROS", "emprestimo_parcela", "PARCELA EMPRESTIMO PESSOAL (QUITAR CHEQUE ESPECIAL)", 15, 520, "DIRECT_DEBIT", "6012", dest="BANCO:B"),
               F("TRANSPORTE", "ipva_seguro", "IPVA E SEGURO VEICULO", 15, 1100, "BOLETO", "9311", mes=1, trab=True, dest="DETRAN:ipva"),
               F("LAZER", "streaming", "ASSINATURA STREAMING VIDEO", 18, 39.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING1", instr="cartao")],
        pesos=dict(utensilios_casa=.04, material_escolar=.04, combustivel=.14, mercado=.22, padaria=.05, restaurante=.08, delivery=.05, farmacia=.05, consulta=.03, cinema_show=.03, bar=.04, marketplace=.04, pix_familia=.04, curso_online=.02, pedagio_estacionamento=.02, passeio=.04, manutencao_veiculo=.03, reparo=.03),
        trab_subs={"combustivel", "manutencao_veiculo", "pedagio_estacionamento", "ipva_seguro"}, noturno_p={},
        bets=dict(tipo="casual", sessoes_noite=.3, bets_por_sessao=(1, 2), stake_med=30, escalada=.1, apos_repasse_p=0,
                  premio_p=.1, aut=.85, nao_aut=.05, interm=.10, via_filho=False),
        fraude=dict(eps_ano=5.0, tipos=dict(boleto_falso=.4, loja_falsa=.3, golpe_investimento=.3)),
        impulso=dict(taxa=.4, parc_p=.3), hn=dict(viagem=.15)),
    "lucas_19": dict(
        nome="Lucas", idade=19, arquetipo="jovem_primeiro_cartao", regime="Estagio", escolaridade=4, score=500,
        vuln=.55, renda_ref=1400, saldo_ini=120, saldo_alvo=120, cheque_limite=200, p_total=.60, p_mora=.12,
        var_frac=.38, cartao_share=.70, contas=["LUCAS_CC_A"], cartoes={"LUCAS_CARTAO_1": (1200, 300)},
        renda=[R("fixa", dia=5, valor=1400, desc="CREDITO BOLSA ESTAGIO EMPRESA LOGISTICA", pm="PIX", h=(9, 10), dest="EMP:ESTAGIO")],
        fixos=[F("EDUCACAO", "mensalidade", "MENSALIDADE FACULDADE ADS", 10, 380, "BOLETO", "8220", dest="EMP:FACULDADE"),
               F("UTILIDADES", "celular", "PLANO CELULAR", 12, 49.9, "CREDIT_CARD", "4814", dest="CONC:celular", instr="cartao"),
               F("LAZER", "streaming", "ASSINATURA STREAMING VIDEO", 18, 29.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING1", instr="cartao"),
               F("LAZER", "streaming", "ASSINATURA STREAMING MUSICA", 20, 19.9, "CREDIT_CARD", "4899", dest="EMP:STREAMING2", instr="cartao")],
        pesos=dict(utensilios_casa=.02, material_escolar=.04, bilhete_transporte=.15, app_transporte=.08, padaria=.07, restaurante=.06, delivery=.08, jogos_eletronicos=.08, marketplace=.08, eletronicos_online=.04, moda=.05, bar=.06, cinema_show=.04, pix_amigo=.08, pix_familia=.02, curso_online=.03, farmacia=.02, mercado=.04, software_pessoal=.03),
        trab_subs=set(), noturno_p=dict(delivery=.2, bar=.1),
        bets=dict(tipo="casual", sessoes_noite=1.0, bets_por_sessao=(1, 3), stake_med=20, escalada=.2, apos_repasse_p=.3,
                  premio_p=.1, aut=.6, nao_aut=.25, interm=.15, via_filho=False),
        fraude=dict(eps_ano=8.0, tipos=dict(loja_falsa=.5, falso_emprestimo=.15, cartao_clonado=.2, golpe_pix_beneficio=.15)),
        impulso=dict(taxa=1.4, parc_p=.5), hn=dict(games=.9, nome_bet=.4)),
    "fernanda_46": dict(
        nome="Fernanda", idade=46, arquetipo="demitida_rescisao", regime="CLT -> Seguro-desemprego", escolaridade=4, score=600,
        vuln=.35, renda_ref=4800, saldo_ini=24000, saldo_alvo=12000, cheque_limite=2000, p_total=.9, p_mora=.08,
        var_frac=.22, cartao_share=.50, contas=["FERNANDA_CC_A"], cartoes={"FERNANDA_CARTAO_1": (6000, 900)},
        renda=[R("fixa", dia=5, valor=4800, desc="CREDITO SALARIO EMPRESA INDUSTRIA TEXTIL", pm="PIX", h=(8, 9), ate=(2026, 9), dest="EMP:TEXTIL"),
               R("avulso", itens=[((2026, 10), 1, (9, 0), 13600, "CREDITO VERBAS RESCISORIAS TRCT"),
                                  ((2026, 10), 6, (11, 0), 28900, "CREDITO MULTA FGTS 40 POR CENTO")]),
               R("fixa", dia=20, valor=2500, desc="CREDITO SEGURO DESEMPREGO PARCELA 1", pm="PIX", h=(8, 8), desde=(2026, 10), dest="GOV:SEGURO")],
        fixos=[F("MORADIA", "financiamento", "PRESTACAO FINANCIAMENTO IMOBILIARIO", 10, 1450, "DIRECT_DEBIT", "6513", dest="BANCO:IMOB"),
               F("MORADIA", "condominio", "CONDOMINIO EDIFICIO", 10, 520, "BOLETO", "6513", dest="EMP:CONDOMINIO"),
               F("SAUDE", "plano_saude", "MENSALIDADE PLANO DE SAUDE", 12, 1150, "DIRECT_DEBIT", "6300", dest="EMP:PLANO_SAUDE"),
               F("EDUCACAO", "mensalidade", "MENSALIDADE UNIVERSIDADE FILHO", 8, 890, "BOLETO", "8220", dest="EMP:UNIVERSIDADE"),
               F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 160, "BOLETO", "4900", jit=.12, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 14, 95, "BOLETO", "4900", jit=.1, dest="CONC:agua"),
               F("UTILIDADES", "internet", "INTERNET FIBRA", 15, 125, "DIRECT_DEBIT", "4899", dest="CONC:internet"),
               F("UTILIDADES", "gas", "GAS ENCANADO", 16, 40, "BOLETO", "5984", dest="CONC:gas"),
               F("UTILIDADES", "celular", "PLANO CELULAR", 8, 60, "DIRECT_DEBIT", "4814", dest="CONC:celular"),
               F("EDUCACAO", "curso_online", "CURSO ONLINE REQUALIFICACAO PROFISSIONAL", 15, 89, "CREDIT_CARD", "8299", desde=(2026, 10), dest="EMP:CURSO_REQ", instr="cartao")],
        pesos=dict(utensilios_casa=.04, material_escolar=.03, mercado=.34, padaria=.06, feira=.04, restaurante=.06, delivery=.04, farmacia=.06, consulta=.03, combustivel=.06, cinema_show=.02, marketplace=.04, moda=.03, pix_familia=.05, estetica=.03, reparo=.04, passeio=.02),
        trab_subs={"combustivel"}, noturno_p={}, bets=None,
        fraude=dict(eps_ano=4.0, fraude_escala=2.0, tipos=dict(golpe_investimento=.5, loja_falsa=.3, boleto_falso=.2), fim_p=.7),
        impulso=dict(taxa=.3, parc_p=.3), hn=dict(viagem=.05, servico_novo=.10)),
    "patricia_53": dict(
        nome="Patricia", idade=53, arquetipo="cuidadora_clt_plantoes", regime="CLT 12x36 + plantoes", escolaridade=4, score=560,
        vuln=.60, renda_ref=6650, saldo_ini=400, saldo_alvo=400, cheque_limite=1000, p_total=.50, p_mora=.25,
        var_frac=.40, cartao_share=.50, contas=["PATRICIA_CC_A", "PATRICIA_MAE_CC"], cartoes={"PATRICIA_CARTAO_1": (4000, 1200)},
        renda=[R("fixa", dia=5, valor=3900, desc="CREDITO SALARIO HOSPITAL CLT", pm="PIX", h=(8, 9), dest="EMP:HOSPITAL"),
               R("plantao_extra", med=450, desc="RECEBIMENTO PLANTAO EXTRA HOSPITAL"),
               R("fixa", dia=10, valor=1850, desc="CONTA DELEGADA MAE BENEFICIO PENSAO POR MORTE INSS", pm="DIRECT_DEBIT", h=(7, 8), dest="INSS", instr="mae")],
        fixos=[F("UTILIDADES", "energia", "CONTA ENERGIA ELETRICA", 12, 210, "BOLETO", "4900", jit=.12, dest="CONC:energia"),
               F("UTILIDADES", "agua", "CONTA AGUA E ESGOTO", 14, 120, "BOLETO", "4900", jit=.1, dest="CONC:agua"),
               F("UTILIDADES", "internet", "INTERNET FIBRA", 15, 100, "DIRECT_DEBIT", "4899", dest="CONC:internet"),
               F("UTILIDADES", "celular", "PLANO CELULAR", 8, 70, "PIX", "4814", dest="CONC:celular"),
               F("UTILIDADES", "gas", "GAS ENCANADO", 16, 70, "BOLETO", "5984", dest="CONC:gas"),
               F("SAUDE", "cuidadora", "CONTA DELEGADA MAE PAGAMENTO CUIDADORA", 5, 800, "PIX", "8099", dest="PF:cuidadora", cnpj=False, instr="mae"),
               F("EDUCACAO", "cursinho", "MENSALIDADE CURSINHO PREVESTIBULAR", 8, 450, "BOLETO", "8299", dest="EMP:CURSINHO"),
               F("DIVIDA_JUROS", "parcelamento_fatura", "PARCELAMENTO FATURA CARTAO 12X", 10, 690, "DIRECT_DEBIT", "6012", dest="BANCO:PARCELAMENTO")],
        pesos=dict(utensilios_casa=.04, material_escolar=.04, mercado=.22, padaria=.04, feira=.03, farmacia=.16, consulta=.04, refeicao_trabalho=.08, app_transporte=.07, combustivel=.06, pix_familia=.04, marketplace=.03, delivery=.03, bilhete_transporte=.03, cinema_show=.01, reparo=.03),
        trab_subs={"refeicao_trabalho", "combustivel"}, noturno_p=dict(refeicao_trabalho=.35, app_transporte=.45, farmacia=.05),
        bets=None,
        fraude=dict(eps_ano=6.0, tipos=dict(falsa_central=.5, loja_falsa=.3, falso_emprestimo=.2),
                    recorrente=dict(meses=8, valores=(92.5, 45.0), dia=2)),
        impulso=dict(taxa=.3, parc_p=.3), hn=dict(viagem=.08, servico_novo=.18)),
}

# --------------------------------------------------------------------------- cenários -> grupo de score
BETA_PARAMS = {
    "normal": (1.3, 15.0), "atipico": (3.5, 6.0), "divida": (3.0, 5.0),
    "bet_regular": (4.0, 3.5), "bet_pos_repasse": (5.0, 2.4), "bet_chasing": (8.0, 1.6), "bet_premio": (2.0, 6.0),
    "impulso": (6.0, 2.0), "rolagem": (5.5, 2.2),
    "fraude_forte": (9.0, 1.5), "fraude_media": (6.0, 2.5), "fraude_sutil": (4.5, 3.0),
}
FRAUDE_FORTE = {"falsa_central", "boleto_falso", "cartao_clonado", "golpe_investimento"}
FRAUDE_SUTIL = {"desconto_indevido"}

NOTAS = {
    "fraude_falsa_central": "Golpe da falsa central: transferencias de alto valor para destinatario novo",
    "fraude_boleto_falso": "Boleto adulterado: beneficiario pessoa fisica divergente do credor",
    "fraude_loja_falsa": "Compra em loja falsa paga por Pix, destinatario novo sem historico",
    "fraude_cartao_clonado": "Compras fora do padrao em sequencia na madrugada (cartao clonado)",
    "fraude_falso_emprestimo": "Taxa antecipada de falso credito liberado",
    "fraude_desconto_indevido": "Desconto recorrente nao autorizado sobre o beneficio",
    "fraude_golpe_investimento": "Promessa de rentabilidade irreal: Pix de alto valor para plataforma nova",
    "fraude_golpe_pix_beneficio": "Falsa taxa de cadastro do beneficio social",
    "bet_regular": "Aposta isolada em horario comum",
    "bet_pos_repasse": "Aposta ate 120 minutos apos receber o repasse ou beneficio",
    "bet_chasing": "Sequencia noturna com escalada de valores (chasing losses)",
    "bet_premio": "Premio recebido de operadora de apostas",
    "impulso_noturno": "Compra noturna por impulso, frequentemente parcelada",
    "rolagem": "Rolagem de divida: fatura de um cartao paga com limite de outro",
    "mora": "Multa e juros de mora por conta paga em atraso",
    "hn_loterica": "Negativo dificil: pagamento de conta em casa lotérica (nao e aposta)",
    "hn_games": "Negativo dificil: loja de jogos eletronicos (nao e aposta)",
    "hn_nome_bet": "Negativo dificil: estabelecimento com 'BET' no nome (nao e aposta)",
    "hn_viagem": "Negativo dificil: compra grande de viagem, parece fraude mas e legitima",
    "hn_servico_novo": "Negativo dificil: Pix alto para prestador novo, parece fraude mas e legitimo",
    "juros_rotativo": "Encargos do rotativo sobre fatura paga parcialmente",
    "juros_cheque": "Juros e IOF do cheque especial no mes anterior",
}

# --------------------------------------------------------------------------- essencialidade
# Primeira regra que casa vence. (arquetipo '*' = qualquer). hora_ini/hora_fim em horas inteiras, com
# janela circular (22 -> 5). trab: True/False/'*' (a transação está ligada ao trabalho da pessoa).
VEIC = "combustivel|manutencao_veiculo|ipva_seguro|pedagio_estacionamento"
REGRAS_ESSENCIALIDADE = [
    dict(regra_id="E01", arquetipo="*", categoria="TRANSPORTE", subtipo=VEIC, recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="True",
         is_essential=True, justificativa="Veiculo usado para trabalhar (entregador, deslocamento ao emprego): sem ele cai a renda"),
    dict(regra_id="E02", arquetipo="*", categoria="TRANSPORTE", subtipo="bilhete_transporte", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Transporte publico: deslocamento basico"),
    dict(regra_id="E03", arquetipo="cuidadora_clt_plantoes", categoria="TRANSPORTE", subtipo="app_transporte", recorrente="*", hora_ini=22, hora_fim=5, valor_max="", trab="*",
         is_essential=True, justificativa="Plantao 12x36: sem transporte publico na madrugada"),
    dict(regra_id="E04", arquetipo="*", categoria="TRANSPORTE", subtipo=VEIC + "|app_transporte", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Uso pessoal ou lazer (inclui app de transporte fora de turno)"),
    dict(regra_id="E10", arquetipo="*", categoria="INSUMO_MEI", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="True",
         is_essential=True, justificativa="Insumo do trabalho do MEI (a mesma compra, feita para uso pessoal, vira LAZER e nao e essencial)"),
    dict(regra_id="E20", arquetipo="*", categoria="SAUDE", subtipo="estetica", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Estetica e discricionaria"),
    dict(regra_id="E21", arquetipo="*", categoria="SAUDE", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Saude, plano, remedios e cuidador: minimo existencial"),
    dict(regra_id="E30", arquetipo="*", categoria="ALIMENTACAO", subtipo="mercado|padaria|feira", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Alimentacao basica"),
    dict(regra_id="E31", arquetipo="gig_economy_apostador|cuidadora_clt_plantoes", categoria="ALIMENTACAO", subtipo="refeicao_trabalho", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Refeicao durante jornada ou plantao: nao ha como levar de casa"),
    dict(regra_id="E32", arquetipo="*", categoria="ALIMENTACAO", subtipo="refeicao_trabalho|restaurante|delivery", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Refeicao fora de casa fora de contexto de turno: discricionaria"),
    dict(regra_id="E40", arquetipo="*", categoria="MORADIA", subtipo="reparo", recorrente="*", hora_ini="", hora_fim="", valor_max=600, trab="*",
         is_essential=True, justificativa="Manutencao basica da moradia ate R$ 600"),
    dict(regra_id="E41", arquetipo="*", categoria="MORADIA", subtipo="reparo", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Reforma acima de R$ 600: nao e essencial"),
    dict(regra_id="E43", arquetipo="*", categoria="MORADIA", subtipo="utensilios_casa", recorrente="*", hora_ini="", hora_fim="", valor_max=150, trab="*",
         is_essential=True, justificativa="Utensilios basicos da casa ate R$ 150"),
    dict(regra_id="E44", arquetipo="*", categoria="MORADIA", subtipo="utensilios_casa", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Moveis, eletrodomesticos e decoracao acima de R$ 150 nao sao minimo existencial"),
    dict(regra_id="E42", arquetipo="*", categoria="MORADIA", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Aluguel, financiamento, condominio e IPTU"),
    dict(regra_id="E50", arquetipo="*", categoria="UTILIDADES", subtipo="tv_assinatura", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="TV por assinatura e discricionaria"),
    dict(regra_id="E51", arquetipo="*", categoria="UTILIDADES", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Luz, agua, gas, internet e celular"),
    dict(regra_id="E60", arquetipo="*", categoria="EDUCACAO", subtipo="mensalidade|cursinho|material_escolar", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Educacao formal da pessoa ou de dependente"),
    dict(regra_id="E61", arquetipo="demitida_rescisao", categoria="EDUCACAO", subtipo="curso_online", recorrente="True", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=True, justificativa="Requalificacao recorrente apos demissao"),
    dict(regra_id="E62", arquetipo="*", categoria="EDUCACAO", subtipo="curso_online", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Curso livre e discricionario"),
    dict(regra_id="E70", arquetipo="*", categoria="LAZER|COMPRAS_IMPULSO", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Lazer e compras por impulso nao entram no minimo existencial"),
    dict(regra_id="E80", arquetipo="*", categoria="|".join(CATEGORIAS_CONTEXTO), subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Classe de contexto: divida, renda, investimento e transferencia nao sao consumo essencial"),
    dict(regra_id="E99", arquetipo="*", categoria="*", subtipo="*", recorrente="*", hora_ini="", hora_fim="", valor_max="", trab="*",
         is_essential=False, justificativa="Padrao: nao essencial"),
]
