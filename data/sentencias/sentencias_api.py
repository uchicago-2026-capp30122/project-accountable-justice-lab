import csv
import datetime
import httpx
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from http_sentencias import cached_get

BASE_DIR = Path(__file__).parent
SENTENCIAS_DIR = BASE_DIR / "sentencias_data"
JSON_SENTENCIAS_DIR = SENTENCIAS_DIR / "_cache"
JSON_SENTENCIAS_DIR_A = JSON_SENTENCIAS_DIR / "_sentencias_json_api"

BASE_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/"
HISTORICAL_ENGROSES = 233075

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


def get_total_ids(url, api_type):
    """
    Get a list of ids from sentencias. Unlike tesis API, this list is not
    sorted, so we cannot loop over ids in order. Instead, we will access a list
    of ids going until page 40 (4,000) records to guarantee we are past year 2025.

    Inputs:
        url (str): base URL for API request
        api_type (str): type of information we are accessing ('tesis' or 'engroses')

    Outputs:
        id_list_total (list): sorted list of ids found in page limit
    """

    id_list_total = []

    page_number = 0

    while page_number <= PAGE_LIMIT:
        if page_number == 0:
            id_list = cached_get(api_type, "ids")
        else:
            kwargs = {"page": str(page_number)}
            id_list = cached_get(api_type, "ids", **kwargs)
        id_list_total.extend(id_list)
        page_number += 1

    return sorted(id_list_total, reverse=True)


def get_id_list(url, api_type, page_number):
    """

    This functions gets list of ids from API, looping over every page number.

    Inputs:
        url (str): base URL for API request
        api_type (str): type of information we are accessing ('tesis' or 'engroses')
    #     page_number (int): page number to access

    # Outputs:
    #     id_list (list): list of ids found in a specific page of the API

    #"""

    # if page_number == 0:
    #     id_list = cached_get(api_type, "ids")
    # else:
    #     kwargs = {"page": str(page_number)}
    #     id_list = cached_get(api_type, "ids", **kwargs)

    # return id_list


def get_all_rulings(url, api_type):
    """

    This function gets all of the sentencia (ruling) records from the list of
    ids found.

    Inputs:
        url (str): base URL for API request
        api_type (str): type of information we are accessing ('tesis' or 'engroses')
        page_number (int): page number to access

    Outputs:
        id_list (list): list of ids found in a specific page of the API

    """

    id_list_total = get_total_ids(BASE_URL, api_type)

    engroses_data_general = []
    counter = 0
    for id_record in id_list_total[0:MAX_RECORDS]:
        print(id_record)
        response = cached_get(api_type, id_record)
        response["fuenteExtraccion"] = "api"
        response["idSentencia"] = id_record
        engroses_data_general.append(response)
        # counter to test a subset of elements
        counter += 1
        if counter == 5:
            break
    print(counter)
    return engroses_data_general


def build_sentencia_csv():
    """
    Create a CSV file populated with columns corresponding to the keys in each
    ruling(json structure). This file will integrate all rulings generated since
    August 2025 that will be accessed through the Supreme Court's API.

    """

    api_type = "engroses"

    engroses_data_general = get_all_rulings(BASE_URL, api_type)

    output_filename = "sentencias_data_api.csv"
    with open(SENTENCIAS_DIR / output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=ENGROSES_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(engroses_data_general)
