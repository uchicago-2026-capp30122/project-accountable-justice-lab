from .tesis.tesis_historical import load_tesis_csv
from .tesis.tesis_api import build_tesis_csv
from .sentencias.sentencias_historical import load_sentencias_csv
from .sentencias.sentencias_api import build_sentencia_csv


def extraction_tesis():
    load_tesis_csv()
    build_tesis_csv()


def extraction_sentencias():
    load_sentencias_csv()
    build_sentencia_csv()


if __name__ == "__main__":
    extraction_tesis()
    extraction_sentencias()
