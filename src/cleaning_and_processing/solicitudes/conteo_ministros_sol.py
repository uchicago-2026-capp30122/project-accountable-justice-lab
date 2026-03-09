"""
conteo_ministros_sol.py
This file builds a year by year time series of minister mentions in solicitudes.
It reads the combined csv, takes each row's description, normalizes the text, 
checks if each minister from the relevant court composition for that year is 
mentioned, counts those matches and writes the result in an output file called 
todos_los_ministros_timeseries.csv. The output is a three column table with 
year, minister and count. This is later used for the bar chart visualization of
solicitudes in streamlit. The order is basically this: load the cleaned 
solicitudes csv, identify the year of each request, look up which ministers     
belonged to the court in that year, check if each minister is mentioned in 
the request text, accumulate counts by minister and year, export the result 
as a CSV for plotting. 


"""

import csv
from pathlib import Path
import sys
from collections import defaultdict

PROJECT_DIR = Path(__file__).resolve().parents[3]

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT / "src" / "analysis" / "solicitudes"))

from salient_tokens_solicitudes import normalize_text, is_mentioning

DEFAULT_CSV = (
    ROOT / "data" / "clean_data" / "solicitudes" / "clean_solicitudes_2017_2026.csv"
)
OUT_DIR = ROOT / "data" / "viz_data"
OUTPUT_CSV = OUT_DIR / "todos_los_ministros_timeseries.csv"


# scjn members per year
INTEGRACION_POR_ANIO = {
    "2017": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "José Ramón Cossío Díaz",
        "Margarita Beatriz Luna Ramos",
        "José Fernando Franco González Salas",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Eduardo Medina Mora",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
    ],
    "2018": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "José Ramón Cossío Díaz",
        "Margarita Beatriz Luna Ramos",
        "José Fernando Franco González Salas",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Eduardo Medina Mora",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
    ],
    "2019": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "José Fernando Franco González Salas",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2020": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "José Fernando Franco González Salas",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2021": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2022": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2023": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "Arturo Zaldívar Lelo de Larrea",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2024": [
        "Luis María Aguilar Morales",
        "Alfredo Gutiérrez Ortiz Mena",
        "Juan Luis González Alcántara Carrancá",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "Lenia Batres Guadarrama",
        "Jorge Mario Pardo Rebolledo",
        "Javier Laynez Potisek",
        "Alberto Pérez Dayán",
        "Norma Lucía Piña Hernández",
        "Margarita Ríos Farjat",
    ],
    "2025": [
        "Hugo Aguilar Ortiz",
        "Lenia Batres Guadarrama",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "María Estela Ríos González",
        "Sara Irene Herrerías Guerra",
        "Giovanni Azael Figueroa Mejía",
        "Irving Espinosa Betanzo",
        "Arístides Rodrigo Guerrero García",
    ],
    "2026": [
        "Hugo Aguilar Ortiz",
        "Lenia Batres Guadarrama",
        "Yasmín Esquivel Mossa",
        "Loretta Ortiz Ahlf",
        "María Estela Ríos González",
        "Sara Irene Herrerías Guerra",
        "Giovanni Azael Figueroa Mejía",
        "Irving Espinosa Betanzo",
        "Arístides Rodrigo Guerrero García",
    ],
}

def run_count():
    """
    Count membership changes over time, 
    so each year uses its own correct list of ministers 
    """
    # creat nested dict structure
    # first key is minister name, second one is year and then value = count
    conteos = defaultdict(lambda: defaultdict(int))
    # nested counter: minister - year - number of matching solicitudes

    with open(DEFAULT_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("year")
            if year not in INTEGRACION_POR_ANIO:
                continue
            # skip rows for years outside the court composition dict
            # normalize request text before checking mentions of minsiter
            clean_text = normalize_text(f"{row.get('DescripcionSolicitud', '')}")

            # only compare against ministers who belonged to court in that year 
            ministros_del_anio = INTEGRACION_POR_ANIO[year]
            for min_name in ministros_del_anio:
                if is_mentioning(clean_text, min_name):
                    conteos[min_name][year] += 1

    print(f"Writing output file ngrams streamlit {OUTPUT_CSV}")
    # one row per year minister combination
    # include all minister year pais, even if 0 so viz data is complete
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "minister", "count"])
        for yr in sorted(INTEGRACION_POR_ANIO.keys(), key=int):
            for min_name in INTEGRACION_POR_ANIO[yr]:
                cuenta = conteos[min_name].get(yr, 0)
                writer.writerow([yr, min_name, cuenta])
    print("Done")


if __name__ == "__main__":
    run_count()

    # uv run src/cleaning_and_processing/solicitudes/conteo_ministros_sol.py
