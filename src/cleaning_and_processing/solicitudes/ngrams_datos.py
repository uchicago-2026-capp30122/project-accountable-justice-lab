import pandas as pd
import csv
from salient_tokens_solicitudes import analyze_themes
from conteo_ministros_sol import INTEGRACION_POR_ANIO

def main():
    csv_path = "clean_output/clean_solicitudes_2017_2026.csv"
    all_minister_results = []
    todos_los_ministros = set()
    for lista in INTEGRACION_POR_ANIO.values():
        todos_los_ministros.update(lista)
    
    print(f"Begin ngrams counts by minister by year")

    for ministro in sorted(todos_los_ministros):
        # 10 ngrams per minister 
        resultados = analyze_themes(csv_path, n_size=2, top_k=10, filter_name=ministro)
        
        if resultados:
            for dato in resultados:
                dato['minister'] = ministro
                all_minister_results.append(dato)
        else:
            print(f"No se encontraron temas para {ministro}")

    # file for streamlit 
    if all_minister_results:
        output_df = pd.DataFrame(all_minister_results)
        output_df = output_df[['year', 'minister', 'ngram', 'count', 'score']]
        output_df.to_csv("ngrams_por_ministro.csv", index=False)
        print("\n Archivo 'ngrams_por_ministro.csv")
    else:
        print("\n No se generaron datos, error con archivo")

if __name__ == "__main__":
    main()