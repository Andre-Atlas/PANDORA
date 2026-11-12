
import re
import unicodedata
import csv
from pathlib import Path

def normalizar_texto(texto):
    """Padroniza textos para facilitar comparações."""
    texto = str(texto or "").upper()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = re.sub(r"[^A-Z0-9]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def normalizar_cnpj(cnpj):
    """Remove caracteres não numéricos do CNPJ."""
    return re.sub(r"\D", "", str(cnpj or ""))


def normalizar_dominio(dominio):
    """Padroniza domínios para comparação."""
    dominio = str(dominio or "").lower().strip()

    dominio = re.sub(r"^https?://", "", dominio)
    dominio = re.sub(r"^www\.", "", dominio)

    dominio = dominio.split("/")[0]
    dominio = dominio.split(":")[0]

    return dominio.strip(".")


def buscar_operadora_por_nome(nome, operadoras):
    """Busca uma operadora pelo nome empresarial ou por suas marcas."""
    nome_normalizado = normalizar_texto(nome)

    if not nome_normalizado:
        return None

    for operadora in operadoras:
        nomes = [
            operadora.get("nome", ""),
            operadora.get("marca", "")
        ]

        nomes.extend(operadora.get("marcas", []))

        for nome_cadastrado in nomes:
            if nome_normalizado == normalizar_texto(nome_cadastrado):
                return operadora

    return None


def verificar_operadora_autorizada(
    nome=None,
    cnpj=None,
    dominio=None,
    operadoras=None
):
    """Verifica se a operadora consta na lista fornecida."""

    operadoras = operadoras or []

    cnpj_normalizado = normalizar_cnpj(cnpj)
    dominio_normalizado = normalizar_dominio(dominio)

    # Busca pelo CNPJ
    if cnpj_normalizado:
        for operadora in operadoras:
            cnpj_cadastrado = normalizar_cnpj(
                operadora.get("cnpj")
            )

            if cnpj_normalizado == cnpj_cadastrado:
                return {
                    "encontrada": True,
                    "autorizada": True,
                    "operadora": operadora,
                    "evidencia": "CNPJ exato"
                }

    # Busca pelo domínio
    if dominio_normalizado:
        for operadora in operadoras:
            dominios = operadora.get("dominios", [])

            for dominio_cadastrado in dominios:
                dominio_cadastrado = normalizar_dominio(
                    dominio_cadastrado
                )

                if dominio_normalizado == dominio_cadastrado:
                    return {
                        "encontrada": True,
                        "autorizada": True,
                        "operadora": operadora,
                        "evidencia": "Domínio exato"
                    }

    # Busca pelo nome ou marca
    if nome:
        resultado = buscar_operadora_por_nome(
            nome,
            operadoras
        )

        if resultado:
            return {
                "encontrada": True,
                "autorizada": True,
                "operadora": resultado,
                "evidencia": "Nome ou marca exatos"
            }

    return {
        "encontrada": False,
        "autorizada": None,
        "operadora": None,
        "evidencia": None
    }

def carregar_operadoras(caminho=None):
    """
    Carrega e agrupa as operadoras do CSV oficial da SPA/MF.
    Uma empresa pode possuir várias marcas e domínios.
    """

    if caminho is None:
        caminho = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "operadoras"
            / "operadoras_spa.csv"
        )

    operadoras = []

    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";")

        # Ignora a descrição inicial e o cabeçalho
        next(leitor)
        next(leitor)

        operadora_atual = None

        for linha in leitor:
            linha += [""] * (7 - len(linha))

            nome = linha[2].strip()
            cnpj = linha[3].strip()
            marca = linha[4].strip()
            dominio = linha[5].strip()
            portaria = linha[1].strip()
            requerimento = linha[6].strip()

            # Nova empresa
            if nome and cnpj:
                operadora_atual = {
                    "nome": nome,
                    "cnpj": cnpj,
                    "marcas": [],
                    "marca": "",
                    "dominios": [],
                    "portaria": portaria,
                    "requerimento": requerimento
                }

                operadoras.append(operadora_atual)

            # Ignora linhas sem empresa anterior
            if operadora_atual is None:
                continue

            # Adiciona marcas e domínios à empresa atual
            if marca and marca not in operadora_atual["marcas"]:
                operadora_atual["marcas"].append(marca)

            if dominio and dominio not in operadora_atual["dominios"]:
                operadora_atual["dominios"].append(dominio)

            # Mantém compatibilidade com o código existente
            if operadora_atual["marcas"]:
                operadora_atual["marca"] = operadora_atual["marcas"][0]

    return operadoras