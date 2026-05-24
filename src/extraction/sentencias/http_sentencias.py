import datetime
import docx2txt

# from docx import Document
import httpx
import json
import time
import re
from datetime import datetime
from pathlib import Path
import subprocess


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw_data"
SENTENCIAS_DIR = RAW_DATA / "sentencias_data"
JSON_SENTENCIAS_DIR = SENTENCIAS_DIR / "_cache"
DOC_SENTENCIAS_DIR = SENTENCIAS_DIR / "_cache_documents"
SOFFICE_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

if not JSON_SENTENCIAS_DIR.is_dir():
    JSON_SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)

if not DOC_SENTENCIAS_DIR.is_dir():
    DOC_SENTENCIAS_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/"

API_TYPE = "engroses"


class FetchException(Exception):
    """
    This function was not made by us but rather obtained from
    code provided by CAPP-122 staff for PA1.

    Turn a httpx.Response into an exception.
    """

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )


def combine_url_with_params(url, params):
    """
    This function was not made by us but rather obtained from
    code provided by CAPP-122 staff for PA1.

    Use httpx.URL to create a URL joined to its parameters. We will use this
    function to add new page for the list of ids of engroses.

    Parameters:
        - url: a URL with or without parameters already
        - params: a dictionary of parameters to add

    Returns:
        The URL with parameters added, for example:

        >>> combine_url_with_params(
            "https://example.com/api/",
            {"api_key": "abc", "page": 2}
        )
        "https://example.com/api/?api_key=abc&page=2"
    """
    url = httpx.URL(url)
    params = dict(url.params) | params  # merge the dicz<tionaries
    return str(url.copy_with(params=params))


def cached_get(record_id, **kwargs) -> dict:
    """
    This function caches all GET requests it makes, by writing
    the successful responses to disk.

    Three things to keep in mind:

    - If the function is making an HTTP request, sleep for 2 seconds first
      using `time.sleep(2)`. (Do not sleep if the response is in cache.)

    Parameters:
        api_type:   will depend on creation of url: {tesis, engroses}
        record_id:  id of tesis or list of ids we will need to access
        **kwargs:   Keyword-arguments that will be appended to the URL as
                    query parameters.

    Returns:
        Contents of response as text.

    Raises:
        FetchException if a non-200 response occurs.
    """

    # Scenario 1: we already have the information stored
    # Create url and remove ignored keys

    url = BASE_URL + API_TYPE + "/" + record_id
    # If we are checking list of ids, information will be stored differently
    if record_id == "ids":
        url = combine_url_with_params(url, kwargs)
        today = datetime.today()
        get_date = str(today.year) + "-" + str(today.month) + "-" + str(today.day)
        get_time = str(today.hour) + "-" + str(today.minute) + "-" + str(today.second)
        filename = get_date + get_time + "_ids" + ".json"
    # Add individual tesis id into one json file
    else:
        filename = record_id + ".json"
    file_path = JSON_SENTENCIAS_DIR / filename
    if file_path.is_file():
        with open(file_path, "r") as f:
            response = json.load(f)
            return response

    # Scenario 2: we don't have the information and need to do a GET request
    else:
        time.sleep(0.5)
        try:
            response = httpx.get(url, follow_redirects=True)
            response.raise_for_status()

            data = response.json()
            with open(file_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data

        except FetchException:
            print("Encountered error while accessing API")


def cached_get_docx(document_url) -> dict:
    """
    This function caches all GET requests it makes, by writing
    the successful responses to disk.

    Three things to keep in mind:

    - If the function is making an HTTP request, sleep for 2 seconds first
      using `time.sleep(2)`. (Do not sleep if the response is in cache.)

    Parameters:
        document_url: url that has document

    Returns:
        Contents of document as text.

    Raises:
        FetchException if a non-200 response occurs.
    """

    # Scenario 1: we already have the information stored
    filename = document_url.split("/")[-1]
    file_path = DOC_SENTENCIAS_DIR / filename

    if file_path.is_file():
        if file_path.suffix == ".doc":
            file_path = convert_to_docx(file_path)
        doc_content = docx2txt.process(file_path)
        return doc_content

    # Scenario 2: we don't have the information and need to do a GET request
    else:
        time.sleep(0.5)
        try:
            response = httpx.get(document_url, follow_redirects=True)
            response.raise_for_status()
            content = response.content

            file_path.write_bytes(content)

            if file_path.suffix == ".doc":
                file_path = convert_to_docx(file_path)

            if file_path.suffix == ".docx":
                doc_content = docx2txt.process(file_path)
                return doc_content
            else:
                return "not found"

        except FetchException:
            print("Encountered error while accessing API")


def convert_to_docx(file_path):
    subprocess.run(
        [
            SOFFICE_PATH,
            "--headless",
            "--convert-to",
            "docx",
            str(file_path),
            "--outdir",
            DOC_SENTENCIAS_DIR,
        ]
    )
    file_path = file_path.with_suffix(".docx")
    return file_path
