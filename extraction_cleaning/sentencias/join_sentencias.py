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
    joined_sentencias = joined_sentencias.drop(columns=["Unnamed: 0"])

    # clean date - extraer año y mes
    joined_sentencias["cleanDate"] = joined_sentencias["fechaResolucion"].apply(
        remove_missing_dates
    )
    joined_sentencias["cleanDate"] = pd.to_datetime(
        joined_sentencias["cleanDate"],
        errors="coerce",
        format="mixed",
        dayfirst=True,
    )

    # extraer votacion
    joined_sentencias["votacion"] = np.where(
        joined_sentencias["pertenencia"] == "Pleno",
        joined_sentencias["votacion"].apply(get_votacion_pleno),
        joined_sentencias["votacion"].apply(get_votacion_salas),
    )

    return joined_sentencias


def get_votacion_pleno(votacion: str):

    pattern_unanimidad = r"(?:[U|u]nanimidad | [O|once] votos | [N|n]ueve votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [O|o]cho votos | [S|s]iete votos | [S|s]eis)"
    votacion_unanimidad = re.search(pattern_unanimidad, votacion)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, votacion)
        if votacion_mayoria:
            return "mayoría"
        else:
            return ""


def get_votacion_salas(votacion: str):

    pattern_unanimidad = r"(?:[U|u]nanimidad | [C|c]inco votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [C|c]uatro votos | [T|t]res votos)"
    votacion_unanimidad = re.search(pattern_unanimidad, votacion)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, votacion)
        if votacion_mayoria:
            return "mayoría"
        else:
            return ""


def remove_missing_dates(date: str):

    if date == "00:00.0":
        return "1900-01-01"
    else:
        return date


if __name__ == "__main__":
    join_sentencias_sources()
