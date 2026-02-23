import csv
import datetime
import httpx
import json
import time
from datetime import datetime
from pathlib import Path
# from .http_scjn import cached_get

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "_cache"
TESIS_DIR = BASE_DIR / "tesis_data"

BASE_URL = "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/"
HISTORICAL_TESIS = 2030777

TESIS_CSV_COLUMNS = (
    "huellaDigital",
    "idTesis",
    "epoca",
    "localizacion",
    "anio",
    "mes",
    "instancia",
    "organoJuris",
    "fuente",
    "materias",
    "tipoTesis",
    "tesis",
    "rubro",
    "texto",
    "precedentes",
    "notaPublica",
    "anexos",
    "fuenteExtraccion",
)


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
    Use httpx.URL to create a URL joined to its parameters, suitable for use
    for cache keys.

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

    - If CACHE_DIR does not yet exist, it should be created using the
     `mkdir` method on `Path`.
    - If the function is making an HTTP request, sleep for 0.5 seconds first
      using `time.sleep(0.5)`. (Do not sleep if the response is in cache.)
    - When creating the cache_key this function must
    include all parameters EXCEPT those included in config.IGNORED_KEYS.

    This is to avoid writing your API key to disk hundreds of times.
    A potential security risk if someone were to see those files somehow.

    Parameters:
        type:       will depend on creation of url: {tesis, engroses}
        record_id:  id we will look for as parameter or if it is a list of ids
        **kwargs:   Keyword-arguments that will be appended to the URL as
                    query parameters.

    Returns:
        Contents of response as text.

    Raises:
        FetchException if a non-200 response occurs.
    """

    # Create directory if it doesn't exist yet
    if not CACHE_DIR.is_dir():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Scenario 1: we already have the information stored
    # Create url and remove ignored keys

    url = BASE_URL + api_type + "/" + record_id
    if record_id == "ids":
        url = combine_url_with_params(url, kwargs)
        print(url)
        today = datetime.today()
        get_date = str(today.year) + "-" + str(today.month) + "-" + str(today.day)
        get_time = str(today.hour) + "-" + str(today.minute) + "-" + str(today.second)
        filename = get_date + get_time + "_ids" + ".json"
    else:
        filename = record_id + ".json"
    file_path = CACHE_DIR / filename
    if file_path.is_file():
        with open(file_path, "r") as f:
            response = json.load(f)
            return response

    # Scenario 2: we don't have the information and need to do a GET request
    else:
        time.sleep(2)
        try:
            response = httpx.get(url, follow_redirects=True)
            response.raise_for_status()

            data = response.json()
            with open(file_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data

        except FetchException:
            print("Encountered error while accessing API")


def get_ids_data(url, api_type):
    """
    Docstring for get_ids_data. Get ids and loop over each to get the data

    :param url: Description
    :param api_type: Description
    """

    general_tesis = []
    general_tesis_scjn = []
    # starting point. Base url

    page_number = 0

    while page_number is not None:
        print("starting loop", page_number)
        tesis_data_general, tesis_data_scjn, page_number = get_id_list(
            BASE_URL, api_type, page_number
        )
        general_tesis.extend(tesis_data_general)
        general_tesis_scjn.extend(tesis_data_scjn)
        if page_number is None:
            break
        print("finished loop")
        page_number += 1
        print("new_number = ", page_number)
    #  if page_number == 2:
    #     break

    return general_tesis, general_tesis_scjn


def get_id_list(url, api_type, page_number):
    """
    Docstring for get_ids_data. Get ids and loop over each to get the data

    :param url: Description
    :param api_type: Description
    """

    print("getting id list")
    tesis_data_general = []
    tesis_data_scjn = []
    # starting point. Base url
    print("page number:", page_number)
    if page_number == 0:
        id_list = cached_get(api_type, "ids")
    else:
        kwargs = {"page": str(page_number)}
        print("kwargs:", kwargs)
        id_list = cached_get(api_type, "ids", **kwargs)

    print(id_list)
    counter = 0
    for id_record in id_list:
        print(id_record)
        if int(id_record) <= HISTORICAL_TESIS:
            page_number = None
            break
        response = cached_get(api_type, id_record)
        response["fuenteExtraccion"] = "api"
        if api_type == "tesis":
            if response["instancia"] == "Suprema Corte de Justicia de la Nación":
                tesis_data_scjn.append(response)
        tesis_data_general.append(response)
        # counter to test a subset of elements
        counter += 1
    print(counter)

    return tesis_data_general, tesis_data_scjn, page_number


def build_tesis_csv(output_filename):
    """
    Create a CSV file populated with the following columns:

    Parameters:
        output_filename: Path object representing location to write file.
    """

    api_type = "tesis"
    output_filename = output_filename + ".csv"

    general_tesis, general_tesis_scjn = get_ids_data(BASE_URL, api_type)

    with open(TESIS_DIR / output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=TESIS_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(general_tesis)

    output_filename_scjn = output_filename + "_scjn.csv"
    with open(TESIS_DIR / output_filename_scjn, "w") as f:
        writer = csv.DictWriter(f, fieldnames=TESIS_CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(general_tesis_scjn)
    return
