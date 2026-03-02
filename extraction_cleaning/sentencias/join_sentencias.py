import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

SENTENCIAS_DATA = BASE_DIR / "data" / "sentencias" / "sentencias_data"

csv_sourcefile = SENTENCIAS_DATA / "sentencias_historical_clean.csv"
api_sourcefile = SENTENCIAS_DATA / "sentencias_data_api.csv"


def join_sentencias_sources():

    api_data = pd.read_csv(api_sourcefile, dtype=str)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str)

    #   csv_data = csv_data.drop(columns=["Unnamed: 0"])

    joined_sentencias = pd.concat([csv_data, api_data], ignore_index=True)

    # clean date - extraer año y mes
    # lower case ponente
    # extraer votacion

    return joined_sentencias


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


def filter_by_year(tesis, year: int):
    # Filter by column anio
    tesis_year = tesis[tesis["anio"] >= year]
    return tesis_year


def clean_date():

    sentencias["cleandate"] = pd.to_datetime(
        sentencias["fechaResolucion"], errors="coerce", format="mixed", dayfirst=True
    )
    df["clean_date"] = df["clean_date"].fillna(pd.to_datetime("1900-01-01"))
