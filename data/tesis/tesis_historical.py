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


FILENAME = "Tesis.csv"

BASE_DIR = Path(__file__).parent
TESIS_DIR = BASE_DIR / "tesis_data"
if not TESIS_DIR.is_dir():
    TESIS_DIR.mkdir(parents=True, exist_ok=True)
JSON_TESIS_DIR = TESIS_DIR / "_tesis_json_historical"
if not JSON_TESIS_DIR.is_dir():
    JSON_TESIS_DIR.mkdir(parents=True, exist_ok=True)


def load_tesis():
    """
    Process csv file into a pandas dataframe and rename columns according to API
    structure
    """
    file_path = BASE_DIR / FILENAME
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
    tesis.to_csv(output_file_csv)

    return tesis


def convert_to_json(df, dir_name, filename):
    # Convert any dataframe to json file
    output_file_json = dir_name / filename
    df.to_json(output_file_json, orient="records", force_ascii=False, indent=4)


def check_correct_load(filename):

    # Check that json loaded correctly. this will be a test

    with open(TESIS_DIR / filename) as t:
        tesis_json = json.load(t)

    # assert len(tesis_json) == 310111 - for "tesis_historical.json"
    return len(tesis_json)


def filter_by_instancia(tesis, instancia: str):
    # Filter by column instancia
    tesis_instancia = tesis[tesis["instancia"] == instancia]
    return tesis_instancia


def filter_by_year(tesis, year: int):
    # Filter by column anio
    tesis_year = tesis[tesis["anio"] >= year]
    return tesis_year


def do_everything():

    tesis = load_tesis()

    tesis_scjn = filter_by_instancia(tesis, "Suprema Corte de Justicia de la Nación")
    tesis_scjn_2015 = filter_by_year(tesis_scjn, 2015)

    output_filename = "tesis_scjn_2015.json"
    convert_to_json(tesis_scjn_2015, TESIS_DIR, output_filename)

    # create json files
    create_individual_files(TESIS_DIR / output_filename)


def create_individual_files(general_json_file):

    with open(general_json_file) as t:
        tesis_json_2015 = json.load(t)

    # load each tesis to a json file
    if not JSON_TESIS_DIR.is_dir():
        JSON_TESIS_DIR.mkdir(parents=True, exist_ok=True)

    # mkdir of json files
    tesis_number = 0
    for tesis in tesis_json_2015:
        if tesis["anexos"] is None:
            tesis["anexos"] = "Sin anexos"
        filename = str(tesis["idTesis"]) + ".json"
        file_path = JSON_TESIS_DIR / filename
        with open(file_path, "w") as f:
            json.dump(tesis, f, ensure_ascii=False, indent=4)
        tesis_number += 1
    print(tesis_number)
    # total tesis files: 5374
