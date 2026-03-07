import datetime
import httpx
import json
import time
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).parent

SENTENCIAS_DIR = BASE_DIR / "sentencias_data"
JSON_SENTENCIAS_DIR = SENTENCIAS_DIR / "_cache"

JSON_SENTENCIAS_DIR_A = JSON_SENTENCIAS_DIR / "_sentencias_json_api"
if not JSON_SENTENCIAS_DIR_A.is_dir():
    JSON_SENTENCIAS_DIR_A.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/"


class FetchException(Exception):
    """
    Turn a httpx.Response into an exception.
    """

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )


def combine_url_with_params(url, params):
    """
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


def cached_get(api_type, record_id, **kwargs) -> dict:
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

    url = BASE_URL + api_type + "/" + record_id
    if record_id == "ids":
        url = combine_url_with_params(url, kwargs)
        today = datetime.today()
        get_date = str(today.year) + "-" + str(today.month) + "-" + str(today.day)
        get_time = str(today.hour) + "-" + str(today.minute) + "-" + str(today.second)
        filename = get_date + get_time + "_ids" + ".json"
    else:
        filename = record_id + ".json"
    file_path = JSON_SENTENCIAS_DIR_A / filename
    if file_path.is_file():
        with open(file_path, "r") as f:
            response = json.load(f)
            return response

    # Scenario 2: we don't have the information and need to do a GET request
    else:
        time.sleep(3)
        try:
            response = httpx.get(url, follow_redirects=True)
            response.raise_for_status()

            data = response.json()
            with open(file_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data

        except FetchException:
            print("Encountered error while accessing API")
