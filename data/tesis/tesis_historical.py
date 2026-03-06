import json
import csv
import pandas as pd
import datetime
from datetime import datetime as dt
from pathlib import Path


"""
For this dataframe need to filter by type of court. Because we only
have tesis from both the supreme count and lower courts. For
the purposes of this project, we are only interested in supreme court. 
"""

BASE_DIR = Path(__file__).parent

TESIS_DIR = BASE_DIR / "tesis_data"
if not TESIS_DIR.is_dir():
    TESIS_DIR.mkdir(parents=True, exist_ok=True)

RAW_DATA = TESIS_DIR / "raw_data"
if not TESIS_DIR.is_dir():
    TESIS_DIR.mkdir(parents=True, exist_ok=True)

JSON_TESIS_DIR = TESIS_DIR / "_cache"
if not JSON_TESIS_DIR.is_dir():
    JSON_TESIS_DIR.mkdir(parents=True, exist_ok=True)

JSON_TESIS_DIR_H = JSON_TESIS_DIR / "_tesis_json_historical"
if not JSON_TESIS_DIR_H.is_dir():
    JSON_TESIS_DIR_H.mkdir(parents=True, exist_ok=True)

# Will be located in tesis_data/raw_data
FILENAME = "Tesis.csv"


def load_tesis_csv():
    """
    This function loads the original 'Tesis.csv' file provided by the Supreme
    Court. It updates some information, including column names to be homogeneized
    with the Supreme Court's API structure. After basic cleaning and adding a
    column to identify its source (fuenteExtraccion = 'csv'), integrated data is
    exported to a json and csv file.

    Inputs: None

    Output: tesis (pandas dataframe). This dataframe includes all historical
    tesis up to july 2025.

    """
    file_path = RAW_DATA / FILENAME
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

    # Keep año as the only int type column
    tesis["anio"] = tesis["anio"].astype("int64")

    # Modify NA values for anexos
    tesis["anexos"] = tesis["anexos"].fillna("Sin anexos")

    # Add source of extraction - historical comes from csv files
    tesis["fuenteExtraccion"] = "csv"

    # First convert from pandas df to a json file with new column names
    output_filename = "tesis_historical.json"
    convert_to_json(tesis, TESIS_DIR, output_filename)

    # Convert from pandas df to a csv file with new column names
    output_file_csv = TESIS_DIR / "tesis_historical_clean.csv"
    tesis.to_csv(output_file_csv, index=False)

    return tesis


def convert_to_json(df, dir_name, filename):
    """
    This function converts a pandas dataframe into a json file and saves it in
    a given directory.
    """

    output_file_json = dir_name / filename
    df.to_json(output_file_json, orient="records", force_ascii=False, indent=4)


# this function will be transfered to utils in cleaning
def filter_by_instancia(tesis, instancia: str):
    # Filter by column instancia
    tesis_instancia = tesis[tesis["instancia"] == instancia]
    return tesis_instancia


# this function will be transfered to utils in cleaning
def filter_by_year(tesis, year: int):
    # Filter by column anio
    tesis_year = tesis[tesis["anio"] >= year]
    return tesis_year


def upload_historical_information():
    """
    This function loads the original 'Tesis.csv' file provided by the Supreme
    Court and creates individual files for information related to the Supreme
    Court only (instancia) and from 2015 on. This to avoid the generation of
    hundreds of thousands of json files.

    Inputs: None

    Output: None.
    """

    tesis = load_tesis_csv()

    tesis_scjn = filter_by_instancia(tesis, "Suprema Corte de Justicia de la Nación")
    tesis_scjn_2015 = filter_by_year(tesis_scjn, 2015)

    output_filename = "tesis_scjn_historical_2015.json"
    convert_to_json(tesis_scjn_2015, TESIS_DIR, output_filename)

    # create json files
    create_individual_files(TESIS_DIR / output_filename)


def create_individual_files(general_json_file):
    """
    This function creates individual json files for each tesis record. This
    function can take in any json file that integrates a specific number of tesis.
    For the purposes of this project, we will only convert individual json files
    for tesis by the Supreme Court from 2015 up to july 2025 (for historical data)

    Inputs: None

    Output: None. Generates json files
    """

    with open(general_json_file) as t:
        tesis_json_2015 = json.load(t)

    # create individual json files
    for tesis in tesis_json_2015:
        if tesis["anexos"] is None:
            tesis["anexos"] = "Sin anexos"
        filename = str(tesis["idTesis"]) + ".json"
        file_path = JSON_TESIS_DIR_H / filename
        with open(file_path, "w") as f:
            json.dump(tesis, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    upload_historical_information()
