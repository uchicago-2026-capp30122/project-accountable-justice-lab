from .extraction.tesis.tesis_api import build_tesis_csv
from .extraction.tesis.tesis_historical import load_tesis_csv


if __name__ == "__main__":
    load_tesis_csv()
    build_tesis_csv()
