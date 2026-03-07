from .sentencias_historical import load_sentencias_csv
from .sentencias_api import build_sentencia_csv


if __name__ == "__main__":
    load_sentencias_csv()
    build_sentencia_csv()
