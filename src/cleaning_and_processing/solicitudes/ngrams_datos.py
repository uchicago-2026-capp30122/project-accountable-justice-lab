"""
ngrams_datos.py
This file does theme analysis (ngrams) for all ministers.
It iterates through the list of SCJN ministers per year, filters
requests mentioning each minister and calculates the top 10 n grams
per year. It generates a file called ngrams_por_ministro.csv, which is
the pre-calculated data for the solicitudes ngram dashboard.
"""

import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

sys.path.append(str(ROOT / "src" / "analysis" / "solicitudes"))
sys.path.append(str(ROOT / "src" / "cleaning_and_processing" / "solicitudes"))

from salient_tokens_solicitudes import analyze_themes
from conteo_ministros_sol import INTEGRACION_POR_ANIO


def main():
    csv_path = (
        ROOT / "data" / "clean_data" / "solicitudes" / "clean_solicitudes_2017_2026.csv"
    )
    output_path = ROOT / "data" / "viz_data" / "ngrams_por_ministro.csv"

    all_minister_results = []
    todos_los_ministros = set()
    for lista in INTEGRACION_POR_ANIO.values():
        todos_los_ministros.update(lista)

    print(f"Begin ngrams counts by minister by year in file {csv_path.name}")

    for ministro in sorted(todos_los_ministros):
        # 10 ngrams per minister
        resultados = analyze_themes(csv_path, n_size=2, top_k=10, filter_name=ministro)

        if resultados:
            for dato in resultados:
                dato["minister"] = ministro
                all_minister_results.append(dato)
        else:
            print(f"Nothing found for this minister {ministro}")

    # file for streamlit
    if all_minister_results:
        output_df = pd.DataFrame(all_minister_results)
        output_df = output_df[["year", "minister", "ngram", "count", "score"]]
        output_df.to_csv(output_path, index=False)
        print("\n file generated: 'ngrams_por_ministro.csv")
    else:
        print("\n Data not generated, error with input file")


if __name__ == "__main__":
    main()

# uv run src/cleaning_and_processing/solicitudes/ngrams_datos.py
