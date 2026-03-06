import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

BASE_DIR = Path(__file__).parent.parent.parent

SENTENCIAS_DATA = BASE_DIR / "data" / "sentencias" / "sentencias_data"

csv_sourcefile = SENTENCIAS_DATA / "sentencias_historical_clean.csv"
api_sourcefile = SENTENCIAS_DATA / "sentencias_data_api.csv"


def join_sentencias_sources():

    api_data = pd.read_csv(api_sourcefile, dtype=str, index_col=0)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str, index_col=0)

    #   csv_data = csv_data.drop(columns=["Unnamed: 0"])

    joined_sentencias = pd.concat([csv_data, api_data], ignore_index=True)

    joined_sentencias["expediente"] = joined_sentencias["expediente"].apply(str)
    joined_sentencias["expediente"] = joined_sentencias["expediente"].apply(clean_date)
    joined_sentencias["expedienteOrigen"] = joined_sentencias["expedienteOrigen"].apply(
        str
    )
    joined_sentencias["expedienteOrigen"] = joined_sentencias["expedienteOrigen"].apply(
        clean_date
    )

    joined_sentencias["cleanDate"] = joined_sentencias["fechaResolucion"].apply(
        remove_missing_dates
    )
    joined_sentencias["cleanDate"] = pd.to_datetime(
        joined_sentencias["cleanDate"],
        errors="coerce",
        format="mixed",
        dayfirst=True,
    )

    # # clean date - extraer año y mes
    joined_sentencias["ministro_clean"] = joined_sentencias["ministro"].apply(
        clean_ministro_name
    )
    joined_sentencias["anio"] = joined_sentencias["cleanDate"].dt.year.astype("Int64")
    mask = joined_sentencias["anio"] == 1900

    joined_sentencias.loc[mask, "anio"] = (
        joined_sentencias.loc[mask, "expediente"]
        .str.extract(r"\b\d{1,4}/(19\d{2}|20\d{2})")[0]
        .astype("Int64")
    )

    joined_sentencias["votos"] = joined_sentencias["votacion"].apply(get_votacion_pleno)

    sentencias_scjn_2015 = filter_by_year(joined_sentencias, 2015)

    output_file_csv = SENTENCIAS_DATA / "sentencias_joined_data.csv"
    sentencias_scjn_2015.to_csv(output_file_csv, index=False)

    return sentencias_scjn_2015


def get_votacion_pleno(votacion: str):

    if votacion == "":
        return "sin datos"
    else:
        pattern_unanimidad = r"(?i)\bunanimidad\b"
        pattern_mayoria = r"(?i)\bmayor[ií]a\b"
        votacion_unanimidad = re.search(pattern_unanimidad, str(votacion))
        if votacion_unanimidad:
            return "unanimidad"
        else:
            votacion_mayoria = re.search(pattern_mayoria, str(votacion))
            if votacion_mayoria:
                return "mayoría"
            else:
                return "otros"


def remove_missing_dates(date: str):

    if date == "00:00.0":
        return "1900-01-01"
    else:
        return date


def filter_by_year(sentencias, year: int):
    # Filter by column anio
    sentencias_year = sentencias[sentencias["anio"] >= year]
    return sentencias_year


def clean_date(file: str):
    """
    Helper function to edit file numbers that were incorrectly converted to
    dates in original data source. For example, file number 02/2022 was converted
    to 'Feb-22'. This regex looks for strings in specific file number columns
    that contain letters and replaces the date structure to a string with
    corresponding file name. Example: from 'Feb-22' to '02/2022'

    Inputs: file (str): file number in string format.

    Output: file (str): same file number but correctly formatted (i.e. eliminating
                        date format)
    """

    pattern = r"^[A-Z][a-z]+"
    match = re.search(pattern, file)
    if match:
        format_string = "%b-%y"
        date_object = dt.strptime(file, format_string)
        formatted_date = date_object.strftime("%m/%Y")
        return formatted_date
    else:
        return file


def extract_year(file: str):

    pattern = r"\b\d{1,4}/(\d{4})"
    match = re.search(pattern, file)
    if match:
        return int(match.group(1))
    return 0


def clean_ministro_name(ministro: str):

    return ministro.lowerr().strip()


if __name__ == "__main__":
    join_sentencias_sources()
