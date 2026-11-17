"""Dados de referência das personas e séries oficiais SGS/BCB para os agentes."""
from __future__ import annotations

from typing import Any

SERIES_SGS_BCB: dict[str, dict[str, Any]] = {
    "22022": {
        "nome": "Taxa média de juros — PF — Cartão de crédito rotativo",
        "valor_referencia": 435.9,
        "unidade": "% a.a.",
    },
    "25467": {
        "nome": "Taxa média mensal de juros — PF — Crédito pessoal consignado INSS",
        "valor_referencia": 24.5,
        "unidade": "% a.a.",
    },
    "432": {
        "nome": "Taxa de juros — Meta Selic definida pelo Copom",
        "valor_referencia": 14.25,
        "unidade": "% a.a.",
    },
    "12": {
        "nome": "Taxa de juros — CDI",
        "valor_referencia": 14.15,
        "unidade": "% a.a.",
    },
    "433": {
        "nome": "IPCA — Variação mensal",
        "valor_referencia": 0.45,
        "unidade": "% a.m.",
    },
}

PERFIS_PERSONAS: dict[str, dict[str, Any]] = {
    "carla_34": {
        "persona_id": "carla_34",
        "nome": "Carla Mendes",
        "idade": 34,
        "arquetipo": "Superendividamento Estrutural Familiar e Defesa do Mínimo Existencial",
        "renda_mensal": 2850.00,
        "minimo_existencial": 2100.00,
        "tom_comunicacao": "acolhedor_simples",
        "dividas": [
            {
                "credor": "Concessionaria Energia (Luz)",
                "modalidade": "servico_essencial",
                "saldo": 360.00,
                "cet_anual_pct": 12.0,
                "parcela_mensal": 360.00,
                "dias_atraso": 45,
                "essencial": True,
            },
            {
                "credor": "Cartao de Credito (Banco A)",
                "modalidade": "rotativo_cartao",
                "saldo": 4200.00,
                "cet_anual_pct": 448.0,
                "parcela_mensal": 630.00,
                "dias_atraso": 0,
                "essencial": False,
            },
            {
                "credor": "Emprestimo Pessoal (Financeira B)",
                "modalidade": "emprestimo_pessoal",
                "saldo": 5800.00,
                "cet_anual_pct": 112.0,
                "parcela_mensal": 480.00,
                "dias_atraso": 0,
                "essencial": False,
            },
        ],
    },
    "diego_24": {
        "persona_id": "diego_24",
        "nome": "Diego Oliveira",
        "idade": 24,
        "arquetipo": "Transtorno do Jogo Online (Bets) e Intervenção Comportamental Empática",
        "renda_mensal": 1120.00,
        "renda_mensal_estimada": 3100.00,
        "minimo_existencial": 515.00,
        "tom_comunicacao": "parceiro_sem_julgamento",
        "dividas": [],
    },
    "antonio_67": {
        "persona_id": "antonio_67",
        "nome": "Sr. Antônio Ferreira",
        "idade": 67,
        "arquetipo": "Vulnerabilidade Digital, Golpes no Pix/Boleto e Proteção Previdenciária",
        "renda_mensal": 2412.00,
        "minimo_existencial": 1650.00,
        "tom_comunicacao": "acessivel_idoso",
        "dividas": [
            {
                "credor": "Consignado INSS Contrato 04",
                "modalidade": "consignado_inss",
                "saldo": 18000.00,
                "cet_anual_pct": 26.8,
                "parcela_mensal": 723.60,
                "dias_atraso": 0,
                "essencial": False,
            }
        ],
    },
    "mariana_28": {
        "persona_id": "mariana_28",
        "nome": "Mariana Costa",
        "idade": 28,
        "arquetipo": "Renda Variável (MEI), Compras por Impulso (BNPL) e Fragmentação em 4 Cartões",
        "renda_mensal": 3200.00,
        "minimo_existencial": 2100.00,
        "tom_comunicacao": "pratico_estruturado",
        "dividas": [
            {
                "credor": "Cartoes Digitais Consolidados",
                "modalidade": "parcelado_cartao",
                "saldo": 6450.00,
                "cet_anual_pct": 79.4,
                "parcela_mensal": 2150.00,
                "dias_atraso": 0,
                "essencial": False,
            }
        ],
    },
    "julia_31": {
        "persona_id": "julia_31",
        "nome": "Júlia Santos",
        "idade": 31,
        "arquetipo": "Reconstrução Pós-Dívida, Ansiedade de Recaída e Educação sob Guardrails CVM",
        "renda_mensal": 4500.00,
        "minimo_existencial": 2800.00,
        "capacidade_poupanca": 500.00,
        "meta_reserva_6_meses": 16800.00,
        "tom_comunicacao": "educativo_calmo",
        "dividas": [],
    },
    "rosangela_43": {
        "persona_id": "rosangela_43",
        "nome": "Rosângela Souza",
        "idade": 43,
        "arquetipo": "Proteção do Benefício Social e Dano Colateral das Bets na Família",
        "renda_mensal": 1560.00,
        "minimo_existencial": 1400.00,
        "tom_comunicacao": "acolhedor_simples",
        "dividas": [],
    },
    "rafael_39": {
        "persona_id": "rafael_39",
        "nome": "Rafael Martins",
        "idade": 39,
        "arquetipo": "Cheque Especial Crônico e Troca de Dívida Cara por Barata",
        "renda_mensal": 5200.00,
        "minimo_existencial": 3600.00,
        "tom_comunicacao": "analitico_direto",
        "dividas": [],
    },
    "lucas_19": {
        "persona_id": "lucas_19",
        "nome": "Lucas Andrade",
        "idade": 19,
        "arquetipo": "Primeiro Cartão de Crédito e Golpes em Compras Digitais",
        "renda_mensal": 1400.00,
        "minimo_existencial": 600.00,
        "tom_comunicacao": "didatico_jovem",
        "dividas": [],
    },
    "fernanda_46": {
        "persona_id": "fernanda_46",
        "nome": "Fernanda Rocha",
        "idade": 46,
        "arquetipo": "Choque de Renda por Demissão, Gestão da Rescisão e Decisões sob Pressão",
        "renda_mensal": 2500.00,
        "minimo_existencial": 5590.00,
        "tom_comunicacao": "estruturado_acolhedor",
        "dividas": [],
    },
    "patricia_53": {
        "persona_id": "patricia_53",
        "nome": "Patrícia Nogueira",
        "idade": 53,
        "arquetipo": "Cuidadora: Finanças Delegadas da Mãe Idosa e Sobrecarga Financeira",
        "renda_mensal": 3900.00,
        "minimo_existencial": 3100.00,
        "tom_comunicacao": "pratico_cuidador",
        "dividas": [],
    },
}

PERFIL_PADRAO: dict[str, Any] = {
    "persona_id": "visitante",
    "nome": "Pessoa Usuária",
    "idade": None,
    "arquetipo": "Educação Financeira e Proteção do Orçamento",
    "renda_mensal": 0.0,
    "minimo_existencial": 0.0,
    "tom_comunicacao": "acolhedor_simples",
    "dividas": [],
}

BANCOS_POR_NOME: dict[str, str] = {
    "banco do brasil": "001",
    "santander": "033",
    "banrisul": "041",
    "banco inter": "077",
    "inter": "077",
    "caixa": "104",
    "caixa economica": "104",
    "bradesco": "237",
    "nubank": "260",
    "nu pagamentos": "260",
    "itau": "341",
    "c6": "336",
    "mercado pago": "323",
}

ROTEIRO_MED_PIX: list[str] = [
    "1. Acione imediatamente o MED (Mecanismo Especial de Devolução) no app ou SAC do banco em até 80 dias (Res. BCB nº 147/2021) para bloquear cautelarmente os valores.",
    "2. Separe o ID Fim-a-Fim (E2E) da transferência Pix, o comprovante com data/horário, o boleto suspeito e os prints das mensagens.",
    "3. Registre Boletim de Ocorrência (Delegacia Eletrônica) e abra reclamação no Banco Central (Meu BC) ou Consumidor.gov.br caso o banco negue o protocolo.",
]
