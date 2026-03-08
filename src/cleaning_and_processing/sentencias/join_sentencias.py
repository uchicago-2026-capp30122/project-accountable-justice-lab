import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from utils_sentencias import (
    get_votacion,
    remove_missing_dates,
    clean_file_number,
)

BASE_DIR = Path(__file__).resolve().parents[3]

SENTENCIAS_RAW_DATA = BASE_DIR / "data" / "raw_data" / "sentencias_data"
SENTENCIAS_CLEAN_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"

csv_sourcefile = SENTENCIAS_RAW_DATA / "sentencias_historical_clean.csv"
api_sourcefile = SENTENCIAS_RAW_DATA / "sentencias_data_api.csv"


def join_sentencias_sources():

    api_data = pd.read_csv(api_sourcefile, dtype=str)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str)

    # Join both datasources
    joined_sentencias = pd.concat([csv_data, api_data], ignore_index=True)

    # Verify that all files have the correct format
    joined_sentencias["expediente"] = joined_sentencias["expediente"].apply(str)
    joined_sentencias["expediente"] = joined_sentencias["expediente"].apply(
        clean_file_number
    )
    joined_sentencias["expedienteOrigen"] = joined_sentencias["expedienteOrigen"].apply(
        str
    )
    joined_sentencias["expedienteOrigen"] = joined_sentencias["expedienteOrigen"].apply(
        clean_file_number
    )

    # Lowercase name of justices
    joined_sentencias["ministro"] = joined_sentencias["ministro"].str.lower()

    # Get voting outcome
    joined_sentencias["votos"] = joined_sentencias["votacion"].apply(get_votacion)

    # # Add cleanDate column to extract as much information of years as possible
    joined_sentencias["cleanDate"] = joined_sentencias["fechaResolucion"].apply(
        remove_missing_dates
    )
    joined_sentencias["cleanDate"] = pd.to_datetime(
        joined_sentencias["cleanDate"],
        errors="coerce",
        format="mixed",
        dayfirst=True,
    )

    # Create year column ('anio')
    joined_sentencias["anio"] = joined_sentencias["cleanDate"].dt.year.astype("Int64")
    # For rulings that don't have dates, extract date in file number
    mask = joined_sentencias["anio"] == 1985
    joined_sentencias.loc[mask, "anio"] = (
        joined_sentencias.loc[mask, "expediente"]
        .str.extract(r"\b\d{1,4}/(19\d{2}|20\d{2})")[0]
        .astype("Int64")
    )

    # Save cleaned dataset
    output_file_csv = SENTENCIAS_CLEAN_DATA / "sentencias_joined_data.csv"
    joined_sentencias.to_csv(output_file_csv, index=False)

    return joined_sentencias


if __name__ == "__main__":
    join_sentencias_sources()

# uv run python src/cleaning_and_processing/tesis/join_sentencias.py
