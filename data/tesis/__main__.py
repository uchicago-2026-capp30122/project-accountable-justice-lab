from .tesis_historical import upload_historical_information
from .tesis_api import build_tesis_csv


if __name__ == "__main__":
    upload_historical_information()
    build_tesis_csv()
