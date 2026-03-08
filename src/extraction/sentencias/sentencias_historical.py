import csv
import datetime
import json
import pandas as pd
import re
from datetime import datetime as dt
from pathlib import Path


"""

This file uploads historical information from sentencias (court rulings) provided
by the Supreme Court of Justice in a csv file format. This information was 
physically provided in August 2nd, 2025, so the csv file has sentencias emitted up 
until July 2025 (sentencias are published every week). 

Unlike tesis, for this data source we do not need to filter by type of court,
since the Supreme Court only publishes its own rulings. 

"""

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw_data"
SENTENCIAS_DIR = RAW_DATA / "sentencias_data"

FILENAME = "Sentencia.csv"


def load_sentencias_csv():
    """
    This function loads the original 'Sentencia.csv' file provided by the Supreme
    Court. It updates some information, including column names to be homogeneized
    with the Supreme Court's API structure. After basic cleaning and adding a
    column to identify its source (fuenteExtraccion = 'csv'), integrated data is
    exported to a json and csv file.

    Inputs:
        None

    Output:
        None. Creates json and csv files

    """
    file_path = SENTENCIAS_DIR / FILENAME
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
            # equivalent to url sentencia in API - this is a document
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

    # Remove empty columns from dataframe (we know we have 15 fields)
    cols_to_keep = sentencias.iloc[:, :15].columns
    sentencias = sentencias[cols_to_keep]

    # We need to clean the file number for files that had them transformed to dates
    sentencias["expediente"] = sentencias["expediente"].apply(str)
    sentencias["expediente"] = sentencias["expediente"].apply(clean_file_number)
    sentencias["expedienteOrigen"] = sentencias["expedienteOrigen"].apply(str)
    sentencias["expedienteOrigen"] = sentencias["expedienteOrigen"].apply(
        clean_file_number
    )

    # Modify NA values for asuntosAcumulados
    sentencias["asuntosAcumulados"] = sentencias["asuntosAcumulados"].fillna(
        "Sin asuntos acumulados"
    )
    # Add source of extraction - historical comes from csv files
    sentencias["fuenteExtraccion"] = "csv"

    # First convert from pandas df to a json file with new column names
    output_filename = "sentencias_historical.json"
    convert_to_json(sentencias, SENTENCIAS_DIR, output_filename)

    # Convert from pandas df to a csv file with new column names.
    output_file_csv = SENTENCIAS_DIR / "sentencias_historical_clean.csv"
    sentencias.to_csv(output_file_csv, index=False)

    return sentencias


def convert_to_json(df, dir_name, filename):
    """
    This function converts a pandas dataframe into a json file and saves it in
    a given directory.

    Inputs:
        - df (pandas dataframe): pandas dataframe to convert into json file
        - dir_name (Path):  path of directory to locate json file
        - filename (str): name of the filename that will store the json file

    Returns:
        None. Stores json file in selected directory

    """

    output_file_json = dir_name / filename
    df.to_json(output_file_json, orient="records", force_ascii=False, indent=4)


def clean_file_number(file: str):
    """
    Helper function to edit file numbers that were incorrectly converted to
    dates in original data source. For example, file number 02/2022 was converted
    to 'Feb-22'. This regex looks for strings in specific file number columns
    that contain letters and replaces the date structure to a string with
    corresponding file name. Example: from 'Feb-22' to '02/2022'

    Inputs: file (str): file number in string format.

    Output: file (str): same file number but correctly formatted (i.e. eliminating
                        date format and keeping it in file-like structure)
    """

    # Check if file number starts with a letter
    pattern = r"^[A-Z][a-z]+"
    match = re.search(pattern, file)
    if match:
        # We know the string follows a 'mm-year' format
        format_string = "%b-%y"
        # Extract string as a datetime object
        date_object = dt.strptime(file, format_string)
        # Convert it into a numerical-type date we will consider as file number
        formatted_date = date_object.strftime("%m/%Y")
        return formatted_date
    else:
        # If file starts with number, there is nothing to be done
        return file


if __name__ == "__main__":
    load_sentencias_csv()
