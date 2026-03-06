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

    api_data = pd.read_csv(api_sourcefile, dtype=str, index_col=0)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str, index_col=0)

    #   csv_data = csv_data.drop(columns=["Unnamed: 0"])

    joined_sentencias = pd.concat([csv_data, api_data], ignore_index=True)
    # joined_sentencias = joined_sentencias.drop(columns=["Unnamed: 0"])

    joined_sentencias["cleanDate"] = joined_sentencias["fechaResolucion"].apply(
        remove_missing_dates
    )
    joined_sentencias["cleanDate"] = pd.to_datetime(
        joined_sentencias["cleanDate"],
        errors="coerce",
        format="mixed",
        dayfirst=True,
    )

    # clean date - extraer año y mes
    joined_sentencias["anio"] = joined_sentencias["cleanDate"].dt.year.astype("Int64")
    joined_sentencias["mes"] = joined_sentencias["cleanDate"].dt.month.astype("Int64")

    joined_sentencias["votos"] = joined_sentencias["votacion"].apply(get_votacion_pleno)

    sentencias_scjn_2015 = filter_by_year(joined_sentencias, 2015)

    output_file_csv = SENTENCIAS_DATA / "sentencias_joined_data.csv"
    sentencias_scjn_2015.to_csv(output_file_csv, index=False)

    # return sentencias_scjn_2015


def get_votacion_pleno(votacion: str):

    pattern_unanimidad = r"UNANIMIDAD"
    pattern_mayoria = r"MAYORÍA"
    votacion_unanimidad = re.search(pattern_unanimidad, str(votacion))
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, str(votacion))
        if votacion_mayoria:
            return "mayoría"
        else:
            return "sin datos"


def remove_missing_dates(date: str):

    if date == "00:00.0":
        return "1900-01-01"
    else:
        return date


def filter_by_year(sentencias, year: int):
    # Filter by column anio
    sentencias_year = sentencias[sentencias["anio"] >= year]
    return sentencias_year


if __name__ == "__main__":
    join_sentencias_sources()
