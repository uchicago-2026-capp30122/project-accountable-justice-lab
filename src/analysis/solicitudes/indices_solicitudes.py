"""
indice_solicitudes.py 
This file computes a basic non response rate to all the requests made 
to the court in a given year. 
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CSV = (
    ROOT / "data" / "clean_data" / "solicitudes" / "clean_solicitudes_2017_2026.csv"
)

OUT_DIR = ROOT / "data" / "viz_data"
OUTPUT_CSV = OUT_DIR / "noresponse_index_solicitudes.csv"

def get_no_response(csv_path):
    df = pd.read_csv(csv_path)
    # date column to datetime
    df['FechaSolicitud'] = pd.to_datetime(df['FechaSolicitud'], dayfirst=True, errors='coerce')
    df['year'] = df['FechaSolicitud'].dt.year

    # response indicator (1 if contains "Entrega de información")
    df['response'] = df['Respuesta'].str.contains(
        "Entrega de información", case=False, na=False
    )
    # no response indicator 
    df['no_response'] = df['response'] == False
    # index by year
    index_no_response = (
        df.groupby('year')['no_response']
        .mean()
        .reset_index(name="no_response_index")
    )

    return index_no_response

def main():
    index_no_response = get_no_response(DEFAULT_CSV)
    index_no_response.to_csv(OUTPUT_CSV, index=False)
    print(index_no_response)
    print("created file for viz of no response index")

if __name__ == "__main__":
    main()

     # uv run src/analysis/solicitudes/indices_solicitudes.py
        