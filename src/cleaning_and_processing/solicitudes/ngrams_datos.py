"""
ngrams_datos.py
This file is a precomputation script for the dashboard on streamlit. It loops 
through all ministers that appear in the yearly dictionary of ministers in the 
SCJN and runs the ngram analysis from salient_tokens_solicitudes.py, collects 
the results in one list, converts that list into a pandas dataframe and writes 
the final table to ngrams_por_ministro.csv. That csv will then be used for the 
solicitudes ngram dashboard. 
"""

import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

sys.path.append(str(ROOT / "src" / "analysis" / "solicitudes"))
sys.path.append(str(ROOT / "src" / "cleaning_and_processing" / "solicitudes"))

from salient_tokens_solicitudes import analyze_themes
from conteo_ministros_sol import INTEGRACION_POR_ANIO
# reuse the same analysis function and the same yearly minister lists 
# so dashboard is consistent 

def main():
    csv_path = (
        ROOT / "data" / "clean_data" / "solicitudes" / "clean_solicitudes_2017_2026.csv"
    )
    output_path = ROOT / "data" / "viz_data" / "ngrams_por_ministro.csv"
    # store all minister level ngram results, then they will be turned into data frame
    all_minister_results = []
    # collect unique set of ministers across all yearly court compositions 
    todos_los_ministros = set()
    for lista in INTEGRACION_POR_ANIO.values():
        todos_los_ministros.update(lista)

    print(f"Begin ngrams counts by minister by year in file {csv_path.name}")

    for ministro in sorted(todos_los_ministros):
        # run the main salience analysis for each minister
        # 10 bigrams per minister
        resultados = analyze_themes(csv_path, n_size=2, top_k=10, filter_name=ministro)

        if resultados:
            for dato in resultados:
                dato["minister"] = ministro
                all_minister_results.append(dato)
        else:
            # if minister not in any solicitudes descriptions
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
