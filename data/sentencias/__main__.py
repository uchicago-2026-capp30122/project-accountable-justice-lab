from .sentencias_historical import upload_historical_information
from .sentencias_api import build_sentencia_csv


if __name__ == "__main__":
    upload_historical_information()
    build_sentencia_csv()
