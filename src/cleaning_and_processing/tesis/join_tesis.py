import csv
import numpy as np
import pandas as pd
from pathlib import Path
from utils_tesis import (
    get_ministro,
    get_votacion_pleno,
    get_votacion_salas,
    simplify_materia,
)


"""

Because tesis can be emitted by courts other
than the Supreme Court, we will filter by type of court. For the purposes of this
project and given the size of the csv file, we will only keep information 
from the Supreme Court for the clearning and analyzing part of the process.
This is important because further processing functions will account for 
structures, names and concepts that are unique to the Supreme Court and not lower
courts (such as: "ministro/ministra", types of voting, etc.)

"""

BASE_DIR = Path(__file__).parent.parent.parent.parent

TESIS_RAW_DATA = BASE_DIR / "data" / "raw_data" / "tesis_data"
TESIS_CLEAN_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

csv_sourcefile = TESIS_RAW_DATA / "tesis_historical_clean.csv"
api_sourcefile = TESIS_RAW_DATA / "tesis_data_api.csv"


def join_tesis_sources():
    """
    This merges api and csv tesis datasources. It also calls several functions
    that clean up certain columns and creates new columns that are relevant for
    the analysis, such as ministro (justice) and main_materia (main subject).

    Because we will be doing two levels of analysis, we will generate two cleaned
    csv files

    Inputs:
        None.

    Returns:
        None. Creates two files: general tesis cleaned up and general tesis
        filtered by instancia and year.

    """

    api_data = pd.read_csv(api_sourcefile, dtype=str)
    csv_data = pd.read_csv(csv_sourcefile, dtype=str)

    joined_tesis = pd.concat([csv_data, api_data], ignore_index=True)
    # # Keep año as the only int type column
    joined_tesis["anio"] = joined_tesis["anio"].astype("int64")

    # # Modify NA values for anexos
    joined_tesis["anexos"] = joined_tesis["anexos"].fillna("Sin anexos")
    joined_tesis["ministro"] = joined_tesis["precedentes"].apply(get_ministro)

    joined_tesis["votos"] = np.where(
        joined_tesis["organoJuris"] == "Pleno",
        joined_tesis["precedentes"].apply(get_votacion_pleno),
        joined_tesis["precedentes"].apply(get_votacion_salas),
    )

    joined_tesis["main_materia"] = joined_tesis["materias"].apply(simplify_materia)

    output_file_csv = TESIS_CLEAN_DATA / "tesis_joined_data.csv"
    joined_tesis.to_csv(output_file_csv, index=False)


if __name__ == "__main__":
    join_tesis_sources()
