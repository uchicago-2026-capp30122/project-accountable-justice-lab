import datetime
import httpx
import json
import time
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "raw_data"
TESIS_DIR = RAW_DATA / "tesis_data"
JSON_TESIS_DIR = TESIS_DIR / "_cache"

if not JSON_TESIS_DIR.is_dir():
    JSON_TESIS_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/"

API_TYPE = "tesis"


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
    function to add new page for the list of ids of tesis.

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

    Parameters:
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
    file_path = JSON_TESIS_DIR / filename
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
