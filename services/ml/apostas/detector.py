import re
import unicodedata

from rapidfuzz import fuzz, process

from services.ml.apostas.operadoras import (
    carregar_operadoras,
    normalizar_cnpj,
    normalizar_dominio,
    verificar_operadora_autorizada,
)


def normalizar_texto(texto):
    """Padroniza texto para facilitar comparações."""
    texto = str(texto or "").upper()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = re.sub(r"[^A-Z0-9]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def detectar_aposta(mcc, descricao, operadoras=None, cnpj=None, dominio=None):
    """
    Identifica possíveis transações de apostas.

    Evidências:
    - MCC 7995
    - CNPJ de operadora cadastrada
    - Nome empresarial ou marca de operadora
    - Correspondência aproximada com operadora
    """

    if operadoras is None:
        operadoras = carregar_operadoras()

    descricao_normalizada = normalizar_texto(descricao)
    mcc = str(mcc or "").strip()

    evidencias = []

    # Regra 1: MCC associado a apostas
    if mcc == "7995":
        evidencias.append({
            "tipo": "mcc",
            "valor": "7995",
            "motivo": "MCC associado a apostas e jogos de azar."
        })

    # Regra 2: Identificação por CNPJ
    cnpj_normalizado = normalizar_cnpj(cnpj) if cnpj else None

    if cnpj_normalizado:
        for operadora in operadoras:
            if not isinstance(operadora, dict):
                continue

            cnpj_operadora = normalizar_cnpj(
                operadora.get("cnpj", "")
            )

            if cnpj_normalizado == cnpj_operadora:
                evidencias.append({
                    "tipo": "cnpj",
                    "valor": cnpj_normalizado,
                    "pontuacao": 100,
                    "motivo": "CNPJ correspondente a uma operadora cadastrada."
                })
                break

    # Regra 3: Identificação por nome ou marca
    for operadora in operadoras:

        # Compatibilidade com listas de strings usadas nos testes
        if isinstance(operadora, str):
            nomes = [operadora]
        else:
            nomes = [
                operadora.get("nome", ""),
                operadora.get("marca", "")
            ]

            nomes.extend(operadora.get("marcas", []))

        for nome in nomes:
            nome_normalizado = normalizar_texto(nome)

            if not nome_normalizado or not descricao_normalizada:
                continue

            # Correspondência exata
            if re.search(
                rf"\b{re.escape(nome_normalizado)}\b",
                descricao_normalizada
            ):
                evidencias.append({
                    "tipo": "operadora",
                    "valor": nome,
                    "pontuacao": 100,
                    "motivo": "Nome de operadora encontrado na descrição."
                })
                break

            # Correspondência aproximada
            palavras_descricao = descricao_normalizada.split()
            palavras_marca = nome_normalizado.split()

            tamanho = len(palavras_marca)

            trechos = [
                " ".join(
                    palavras_descricao[i:i + tamanho]
                )
                for i in range(
                    len(palavras_descricao) - tamanho + 1
                )
            ]

            resultado = process.extractOne(
                nome_normalizado,
                trechos,
                scorer=fuzz.ratio,
                score_cutoff=90
            )

            if resultado:
                _, pontuacao, _ = resultado

                evidencias.append({
                    "tipo": "operadora",
                    "valor": nome,
                    "pontuacao": pontuacao,
                    "motivo": "Possível correspondência aproximada com operadora."
                })
                break

    # Regra 4: Identificação por domínio
    dominio_normalizado = normalizar_dominio(dominio) if dominio else None

    if dominio_normalizado:
        for operadora in operadoras:
            if not isinstance(operadora, dict):
                continue

            dominios = operadora.get("dominios", [])

            for dominio_operadora in dominios:
                dominio_cadastrado = normalizar_dominio(dominio_operadora)

                if dominio_normalizado == dominio_cadastrado:
                    evidencias.append({
                        "tipo": "dominio",
                        "valor": dominio_normalizado,
                        "pontuacao": 100,
                        "motivo": "Domínio correspondente a uma operadora cadastrada."
                    })
                    break
            else:
                continue

            break

    # Verifica se a operadora consta na base oficial
    operadoras_cadastradas = [
        operadora
        for operadora in operadoras
        if isinstance(operadora, dict)
    ]

    nome_identificado = next(
        (
            evidencia["valor"]
            for evidencia in evidencias
            if evidencia["tipo"] == "operadora"
        ),
        None
    )

    autorizacao = verificar_operadora_autorizada(
        nome=nome_identificado,
        cnpj=cnpj,
        dominio=dominio,
        operadoras=operadoras_cadastradas
    )

    return {
        "is_bet": bool(evidencias),
        "evidencias": evidencias,
        "autorizacao": autorizacao
    }