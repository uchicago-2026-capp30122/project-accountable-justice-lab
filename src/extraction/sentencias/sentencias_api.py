import csv
import datetime
import httpx
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from .http_sentencias import cached_get

"""
This file gets sentencias (court rulings) most recent information from the Supreme
Court's API. This information will only be accessed for sentencias emitted after 
July 2025, since everything before that has been provided via csv file. 

Unlike tesis that had progressive id's, in the case of sentencias, larger ids 
do not necessarily mean they are more recent, although there is not a big 
variation between numbers. Because of this, we must treat tesis and sentencias 
APIs differently. In this case, we will first get a complete list of ids up to
a reasonable limit of page numbers that contain IDs and number of records. 
This was previously analyzed and considers a rough estimate of rulings that 
correspond to information before july 2025 and we know we have historically
saved in our csv file "Sentencia.csv" provided by the Supreme Court. 

"""

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw_data"
SENTENCIAS_DIR = RAW_DATA / "sentencias_data"

# Checking limits for sentencias ids - looking for those post July 2025
PAGE_LIMIT = 40
MAX_RECORDS = 1000

ENGROSES_CSV_COLUMNS = (
    "idSentencia",
    "expediente",
    "pertenencia",
    "ministro",
    "tema",
    "organoJurisdiccionalOrigen",
    "organoResolvio",
    "fechaResolucion",
    "resolucion",
    "urlInternet",
    "votacion",
    "asuntosAcumulados",
    "huellaDigital",
    "fuenteExtraccion",
)


def get_total_ids():
    """
    Get a list of ids from sentencias. Unlike tesis API, this list is not
    sorted, so we cannot loop over ids in order. Instead, we will access a list
    of ids going until page 40 (4,000) records to guarantee we are past year 2025.

    Inputs:
        None

    Outputs:
        id_list_total (list): sorted list of ids found in page limit
    """

    id_list_total = []

    page_number = 0

    while page_number <= PAGE_LIMIT:
        if page_number == 0:
            id_list = cached_get("ids")
        else:
            kwargs = {"page": str(page_number)}
            id_list = cached_get("ids", **kwargs)
        id_list_total.extend(id_list)
        page_number += 1

    return sorted(id_list_total, reverse=True)


def get_all_rulings():
    """

    This function gets all of the sentencias (rulings) records from the list of
    ids found. It loops through all of the ids found in the initial list and
    will only add the information if the date of the ruling is newer than
    July 9, 2025 (which is the last information we have in our historical csv
    file)

    Inputs:
        None

    Outputs:
        id_list (list): list of ids found in a specific page of the API

    """

    id_list_total = get_total_ids()

    engroses_data_general = []

    # We will limit loop to maximum records that we know are older than 2025
    for id_record in id_list_total[0:MAX_RECORDS]:
        response = cached_get(id_record)
        # Only add records after July 2025
        if datetime.strptime(
            response["fechaResolucion"], "%d/%m/%Y"
        ) > datetime.strptime("09/07/2025", "%d/%m/%Y"):
            response["fuenteExtraccion"] = "api"
            response["idSentencia"] = id_record
            engroses_data_general.append(response)

    return engroses_data_general


def build_sentencia_csv():
    """
    Create a CSV file populated with columns corresponding to the keys in each
    ruling(json structure). This file will integrate all rulings generated since
    August 2025 that will be accessed through the Supreme Court's API.

    """

    engroses_data_general = get_all_rulings()

    output_filename = "sentencias_data_api.csv"
    with open(SENTENCIAS_DIR / output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=ENGROSES_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(engroses_data_general)


if __name__ == "__main__":
    build_sentencia_csv()
