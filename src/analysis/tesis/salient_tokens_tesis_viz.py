import streamlit as st
import pandas as pd
import altair as alt
import csv
import sys
from pathlib import Path
from collections import Counter
from salient_tokens_tesis import ORDER, analyze_themes

BASE_DIR = Path(__file__).parent.parent.parent.parent
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

SOLICITUDES_COUNTS_CSV = Path("data/viz_data/todos_los_ministros_timeseries.csv")


def render_solicitudes_tab():
    """Renderiza las pestañas de la aplicación."""
    st.header("⚖️ Conceptos más mencionados en tesis")

    # Ngrams

    st.subheader("Conoce la(s) palabra(s) más mencionadas en los rubros de las tesis")

    col1, col2 = st.columns(2)

    with col1:
        selected_epoca_themes = st.selectbox("Época:", ORDER, key="themes_epoca")

    with col2:
        n_size = st.selectbox("Tamaño (n-gram):", [1, 2, 3], index=1)

        top_k = st.slider("Número de conceptos a mostrar:", 3, 15, 8)

        if st.button("Ejecutar Análisis de Temas"):
            try:
                # Llamamos a la función de tu archivo maestro
                data_list = analyze_themes(n_size=n_size, top_k=top_k)

                if data_list:
                    themes_df = pd.DataFrame(data_list)
                    # Filtramos el resultado por el año seleccionado en la UI
                    themes_epoca = themes_df[
                        themes_df["epoca"] == str(selected_epoca_themes)
                    ]

                    display_df = themes_epoca[["ngram", "count", "score"]].rename(
                        columns={
                            "ngram": "Tema (N-gram)",
                            "count": "Frecuencia",
                            "score": "Relevancia (Score)",
                        }
                    )
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
            except FileNotFoundError:
                st.error("Error: missing file")


if __name__ == "__main__":
    # load ngrams
    render_solicitudes_tab()
