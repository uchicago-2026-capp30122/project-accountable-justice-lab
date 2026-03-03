import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

TESIS_DATA = BASE_DIR / "data" / "tesis" / "tesis_data"

csv_sourcefile = TESIS_DATA / "tesis_historical_clean.csv"
api_sourcefile = TESIS_DATA / "tesis_data_api.csv"


def join_tesis_sources():

    api_data = pd.read_csv(api_sourcefile, dtype=str)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str)

    csv_data = csv_data.drop(columns=["Unnamed: 0"])

    joined_tesis = pd.concat([csv_data, api_data], ignore_index=True)
    # Keep año as the only int type column
    joined_tesis["anio"] = joined_tesis["anio"].astype("int64")

    # Modify NA values for anexos
    joined_tesis["anexos"] = joined_tesis["anexos"].fillna("Sin anexos")
    joined_tesis["ministro"] = joined_tesis["precedentes"].apply(get_ministro)

    joined_tesis["votacion"] = np.where(
        joined_tesis["organoJuris"] == "Pleno",
        joined_tesis["precedentes"].apply(get_votacion_pleno),
        joined_tesis["precedentes"].apply(get_votacion_salas),
    )

    joined_tesis["main_materia"] = joined_tesis["materias"].apply(simplify_materia)
    tesis_scjn = filter_by_instancia(
        joined_tesis, "Suprema Corte de Justicia de la Nación"
    )

    tesis_scjn_2015 = filter_by_year(tesis_scjn, 2015)

    return tesis_scjn_2015


def get_ministro(precedentes: str):

    pattern = (
        r"(?<=Ponente:\s)[A-Z][a-záéíóúüñ]+(?:\s[A-Z]\.)*(?:\s[A-Z][a-záéíóúüñ]+)+"
    )
    noise = r"ministr[o|a]\s|president[e|a]\s"
    ministro = re.findall(pattern, precedentes)

    if not ministro:
        return "sin datos"

    ministro = " ".join(ministro).lower()
    return re.sub(noise, "", ministro)


def get_votacion_pleno(precedentes: str):

    pattern_unanimidad = r"(?:[U|u]nanimidad | [O|once] votos | [N|n]ueve votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [O|o]cho votos | [S|s]iete votos | [S|s]eis)"
    votacion_unanimidad = re.search(pattern_unanimidad, precedentes)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, precedentes)
        if votacion_mayoria:
            return "mayoría"
        else:
            return ""


def get_votacion_salas(precedentes: str):

    pattern_unanimidad = r"(?:[U|u]nanimidad | [C|c]inco votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [C|c]uatro votos | [T|t]res votos)"
    votacion_unanimidad = re.search(pattern_unanimidad, precedentes)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, precedentes)
        if votacion_mayoria:
            return "mayoría"
        else:
            return ""

def filter_by_instancia(tesis, instancia: str):
    # Filter by column instancia
    tesis_instancia = tesis[tesis["instancia"] == instancia]
    return tesis_instancia


def filter_by_year(tesis, year: int):
    # Filter by column anio
    tesis_year = tesis[tesis["anio"] >= year]
    return tesis_year


def simplify_materia(materias):

    materia_pattern = r"([A-Za-záéíóúÁÉÍÓÚüÜñÑ]+)"
    materia = re.search(materia_pattern, materias)
    if materia:
        return materia.group()
    else:
        return ""


if __name__ == "__main__":
    join_tesis_sources()
