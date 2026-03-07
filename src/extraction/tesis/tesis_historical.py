import json
import csv
import pandas as pd
import datetime
from datetime import datetime as dt
from pathlib import Path


"""
This file uploads historical information from tesis (legal precedents) provided
by the Supreme Court of Justice in a csv file format. This information was 
physically provided in August 2nd, 2025, so the csv file has tesis emitted up 
until July 2025 (tesis are published every week). 
"""

BASE_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw_data"
TESIS_DIR = RAW_DATA / "tesis_data"

FILENAME = "Tesis.csv"


def load_tesis_csv():
    """
    This function loads the original 'Tesis.csv' file provided by the Supreme
    Court. It updates some information, including column names to be homogeneized
    with the Supreme Court's API structure. After basic cleaning and addition of
    a column to identify its source (fuenteExtraccion = 'csv'), integrated data is
    exported to a json and csv file.

    Inputs: None

    Returns:
        None. Creates json and csv files

    """
    file_path = TESIS_DIR / FILENAME
    # Set all columns to strings
    tesis_original = pd.read_csv(file_path, dtype=str)

    # Change names of columns to homogenize with SCJN API Tesis
    tesis = tesis_original.rename(
        columns={
            "SHA-256": "huellaDigital",
            "Registro Digital": "idTesis",
            "Época": "epoca",
            "Localización": "localizacion",
            "Año": "anio",
            "Mes": "mes",
            "Instancia": "instancia",
            "Órgano": "organoJuris",
            "Publicación": "fuente",
            "Materia": "materias",
            "Tipo de Tesis": "tipoTesis",
            "Número de Identificación": "tesis",
            "Título/Subtítulo": "rubro",
            "Texto": "texto",
            "Precedentes": "precedentes",
            "Nota de publicación": "notaPublica",
            "Anexos": "anexos",
        }
    )

    # Drop possibly empty rows
    tesis = tesis.dropna(how="all")
    # Keep year (anio) as the only int type column
    tesis["anio"] = tesis["anio"].astype("int64")
    # Modify NA values for anexos
    #  tesis["anexos"] = tesis["anexos"].fillna("Sin anexos")
    # Add source of extraction - historical comes from csv files
    tesis["fuenteExtraccion"] = "csv"
    # First convert from pandas df to a json file with new column names
    output_filename = "tesis_historical.json"
    convert_to_json(tesis, TESIS_DIR, output_filename)
    # Convert from pandas df to a csv file with new column names
    output_file_csv = TESIS_DIR / "tesis_historical_clean.csv"
    tesis.to_csv(output_file_csv, index=False)


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


if __name__ == "__main__":
    load_tesis_csv()
