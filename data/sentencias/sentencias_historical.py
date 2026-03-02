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

BASE_DIR = Path(__file__).parent

SENTENCIAS_DIR = BASE_DIR / "sentencias_data"
if not SENTENCIAS_DIR.is_dir():
    SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)

RAW_DATA = SENTENCIAS_DIR / "raw_data"
if not SENTENCIAS_DIR.is_dir():
    SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)

JSON_SENTENCIAS_DIR = SENTENCIAS_DIR / "_cache"
if not JSON_SENTENCIAS_DIR.is_dir():
    JSON_SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)

JSON_SENTENCIAS_DIR_H = JSON_SENTENCIAS_DIR / "_sentencias_json_historical"
if not JSON_SENTENCIAS_DIR_H.is_dir():
    JSON_SENTENCIAS_DIR_H.mkdir(parents=True, exist_ok=True)

# Will be located sentencia_data/raw_data
FILENAME = "Sentencia.csv"


def load_sentencias_csv():
    """
    This function loads the original 'Sentencia.csv' file provided by the Supreme
    Court. It updates some information, including column names to be homogeneized
    with the Supreme Court's API structure. After basic cleaning and adding a
    column to identify its source (fuenteExtraccion = 'csv'), integrated data is
    exported to a json and csv file.

    Inputs: None

    Output: sentencias (pandas dataframe). This dataframe includes all historical
    sentencias up to july 2025.

    """
    file_path = RAW_DATA / FILENAME
    sentencias_original = pd.read_csv(file_path, dtype=str)

    # Change names of columns to homogenize with SCJN API Engroses
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
            "Asuntos acumulados": "asuntosAcumulados",
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

    sentencias["asuntosAcumulados"] = sentencias["asuntosAcumulados"].fillna(
        "Sin asuntos acumulados"
    )
    sentencias["fuenteExtraccion"] = "csv"

    # First convert from pandas df to a json file with new column names

    output_filename = "sentencias_historical.json"
    convert_to_json(sentencias, SENTENCIAS_DIR, output_filename)

    # Convert from pandas df to a csv file with new column names.
    # file I will merge with the one online. csv join
    output_file_csv = SENTENCIAS_DIR / "sentencias_historical_clean.csv"
    sentencias.to_csv(output_file_csv)

    return sentencias


def convert_to_json(df, dir_name, filename):
    """
    This function converts a pandas dataframe into a json file and saves it in
    a given directory.
    """

    output_file_json = dir_name / filename
    df.to_json(output_file_json, orient="records", force_ascii=False, indent=4)


def upload_historical_information():
    """
    This function loads the original 'Sentencia.csv' file provided by the Supreme
    Court and creates individual json files for each ruling. Because the csv
    contains information from the Supreme Court only, in this case, we don't
    need to do a filtering by "instancia" (contrary to tesis)

    Inputs: None

    Output: None
    """

    sentencias = load_sentencias_csv()

    output_filename = "sentencias_scjn_historical_2015.json"
    convert_to_json(sentencias, SENTENCIAS_DIR, output_filename)

    create_individual_files(SENTENCIAS_DIR / output_filename)


def create_individual_files(general_json_file):
    """
    This function creates individual json files for each sentencia (ruling) record.
    This function can take in any json file that integrates a specific number of
    rulings.

    Inputs: None

    Output: None. Generates json files
    """

    with open(general_json_file) as t:
        sentencias_json = json.load(t)

    # create individual json files
    counter = 0
    for sentencia in sentencias_json:
        filename = (
            str(sentencia["expediente"]).replace("/", "-")
            + "__"
            + str(sentencia["tipoAsunto"]).replace(" ", "-")
            + ".json"
        )
        file_path = JSON_SENTENCIAS_DIR_H / filename
        with open(file_path, "w") as f:
            json.dump(sentencia, f, ensure_ascii=False, indent=4)
        counter += 1
        if counter == 20:
            break


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
