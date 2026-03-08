import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from .salient_tokens_tesis import ORDER, analyze_themes, main_ngrams

BASE_DIR = Path(__file__).resolve().parents[3]
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"
tesis_data_file = TESIS_DATA / "tesis_joined_data_scjn.csv"


def render_ngrams_tesis_tab():
    """Renderiza las pestañas de la aplicación."""
    st.header("⚖️ Conceptos más mencionados en tesis")

    # Ngrams

    st.subheader("Conoce la(s) palabra(s) más mencionadas en los rubros de las tesis")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_epoca = st.selectbox("Época:", ORDER, key="themes_epoca")

    with col2:
        n_size = st.selectbox("Tamaño del (n-gram):", [1, 2, 3], index=0)

    with col3:
        top_k = st.slider("Número de resultados", 5, 10, 15)

    if st.button("Ejecutar Análisis de Temas", key="run_themes"):
        try:
            temas_tesis = analyze_themes(
                filename=tesis_data_file,
                n_size=n_size,
                top_k=top_k,
            )

            if temas_tesis.empty:
                st.warning("No se encontraron resultados.")
                return

            temas_epoca = temas_tesis[temas_tesis["epoca"] == selected_epoca].copy()
            # Llamamos a la función de tu archivo maestro

            if temas_epoca.empty:
                st.warning(f"No hay resultados para {selected_epoca}.")
                return

            temas_epoca = temas_epoca.sort_values("score", ascending=False)

            display_temas = temas_epoca[["ngram", "count", "score"]].rename(
                columns={
                    "ngram": "Concepto(s)",
                    "count": "Frecuencia",
                    "score": "Relevancia",
                }
            )
            return st.dataframe(
                display_temas, hide_index=True, use_container_width=True
            )

        except FileNotFoundError:
            st.error("Error: archivo de datos no encontrado")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    render_ngrams_tesis_tab()
