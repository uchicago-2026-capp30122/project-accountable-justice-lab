import csv
from pathlib import Path


BASE_DIR = Path(__file__).parent

ministros_filename = BASE_DIR / "ministros.csv"


def get_ministro_name_list():

    ministros = set()
    with open(ministros_filename, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
           ministros.add(row['Nombre'])
           
    return ministros
