import csv
import datetime
import json
import pandas as pd
import re
from datetime import datetime as dt
from pathlib import Path


"""
For this dataframe we don't need to filter by type of court. Because we only
have supreme court rulings. 
"""


FILENAME = "Sentencia.csv"

BASE_DIR = Path(__file__).parent
SENTENCIAS_DIR = BASE_DIR / "sentencias_data"
if not SENTENCIAS_DIR.is_dir():
    SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)
JSON_SENTENCIAS_DIR = SENTENCIAS_DIR / "_sentencias_json_historical"
if not JSON_SENTENCIAS_DIR.is_dir():
    JSON_SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)


def load_sentencias():
    """
    Process csv file into a pandas dataframe and rename columns according to API
    structure
    """
    file_path = BASE_DIR / FILENAME
    sentencias_original = pd.read_csv(file_path, dtype=str)

    # Change names of columns to homogenize with SCJN API Tesis
    sentencias = sentencias_original.rename(
        columns={
            "Expediente": "expediente",
            "Órgano de Radicación": "pertenencia",
            "Ministra o Ministro": "ministro",
            "Tema": "tema",
            "Órgano Jurisdiccional de Origen": "organoJurisdiccionalOrigen",
            # expediente de origen not in API
            "Expediente de Origen": "expedienteOrigen",
            "Órgano que resolvió": "organoResolvio",
            "Fecha de resolución": "fechaResolucion",
            "Resolutivos": "resolucion",
            # ponente not in API
            "Ponente": "ponente",
            # equivalent to url sentencia - this is a document
            "Documento de Sentencia VP": "documentoSentencia",
            "Votación": "votacion",
            "Asuntos acumulados": "asuntos_acumulados",
            # tipo de asunto not in API
            "Tipo de asunto": "tipoAsunto",
            "Certificado Digital": "huellaDigital",
        }
    )

    # Drop possibly empty rows: (8165) empty rows
    sentencias = sentencias.dropna(how="all")

    # There are lots of empty columns in original CSV. We will keep those that have information
    cols_to_keep = sentencias.iloc[:, :15].columns
    sentencias = sentencias[cols_to_keep]

    # We need to clean the file number for files that had them transformed to dates

    sentencias["expediente"] = sentencias["expediente"].apply(str)
    sentencias["expediente"] = sentencias["expediente"].apply(clean_date)
    sentencias["expedienteOrigen"] = sentencias["expedienteOrigen"].apply(str)
    sentencias["expedienteOrigen"] = sentencias["expedienteOrigen"].apply(clean_date)

    sentencias["asuntos_acumulados"] = sentencias["asuntos_acumulados"].fillna(
        "Sin asuntos acumulados"
    )
    sentencias["fuenteExtraccion"] = "csv"

    # First convert from pandas df to a json file with new column names

    output_filename = "sentencias_historical.json"
    convert_to_json(sentencias, SENTENCIAS_DIR, output_filename)

    # Convert from pandas df to a csv file with new column names.
    # file I will merge with the one online. csv join
    output_file_csv = SENTENCIAS_DIR / "sentencias_scjn_historical_clean.csv"
    sentencias.to_csv(output_file_csv)

    return sentencias


def convert_to_json(df, dir_name, filename):
    # Convert any dataframe to json file
    output_file_json = dir_name / filename
    df.to_json(output_file_json, orient="records", force_ascii=False, indent=4)


def check_correct_load(filename):

    # Check that json loaded correctly. this will be a test

    with open(SENTENCIAS_DIR / filename) as t:
        sentencias_json = json.load(t)

    # assert len(tesis_json) == 112242 - for "sentencias_historical.json"
    return len(sentencias_json)


def get_date(sentencia):
    # creo que la puedo borrar

    date = sentencia["fechaResolucion"]
    format_string = "%d/%m/%y %I:%M"
    date_object = dt.strptime(date, format_string)
    return date_object.day, date_object.month, date_object.year


def main():
    """
    This will be __main__()
    """

    sentencias = load_sentencias()
    output_filename = "sentencias_historical.json"

    create_individual_files(SENTENCIAS_DIR / output_filename)
    # create json files


def create_individual_files(general_json_file):

    with open(general_json_file) as t:
        sentencias_json = json.load(t)

    # mkdir of json files
    sentencia_number = 0
    for sentencia in sentencias_json:
        #     day, month, year = get_date(sentencia)
        filename = (
            str(sentencia["expediente"]).replace("/", "-")
            #      str(sentencia["pertenencia"])
            + "__"
            + str(sentencia["tipoAsunto"]).replace(" ", "-")
            #   + "_"
            #  + str(year)
            #  + "_"
            #   + str(month)
            #   + "_"
            #   + str(day)
            + ".json"
        )
        file_path = JSON_SENTENCIAS_DIR / filename
        with open(file_path, "w") as f:
            json.dump(sentencia, f, ensure_ascii=False, indent=4)
        sentencia_number += 1
    print(sentencia_number)
    # total sentencia files: rows 104077 - files: 10477 - creo que hay sentencias repetidas


def clean_date(string):
    pattern = r"^[A-Z][a-z]+"
    match = re.search(pattern, string)
    if match:
        format_string = "%b-%y"
        date_object = dt.strptime(string, format_string)
        formatted_date = date_object.strftime("%m/%Y")
        return formatted_date
    else:
        return string


if __name__ == "__main__":
    main()
