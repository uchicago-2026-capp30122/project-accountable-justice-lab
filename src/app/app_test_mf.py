## streamlit run src/app/app_test.py

import sys
from pathlib import Path

# Allow imports from src/
ROOT_PATH = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(ROOT_PATH))

import streamlit as st
import pandas as pd


from analysis.tesis.tesis_graphs import get_all_tesis_charts
from analysis.tesis.tesis_productivity_index import get_productivity_ministros_app
from analysis.tesis.salient_tokens_tesis_viz import render_ngrams_tesis_tab

from analysis.sentencias.sentencias_graphs import get_all_sentencias_charts

# PAGE CONFIG
st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.title("⚖️ OJO PIOJO")
st.write("Accountable Justice Lab")
##st.image("frontend/ojopiojo.jpeg", width=120)


(
    total_tesis,
    tesis_timeline_chart,
    tesis_por_tipo_chart,
    tesis_materias_chart,
    tesis_heatmap,
) = get_all_tesis_charts()
(
    total_sentencias,
    sentencias_timeline_chart,
    sentencias_votacion_chart,
    sentencias_heatmap,
) = get_all_sentencias_charts()

# MAIN TABS
tab_general, tab_solicitudes, tab_sentencias, tab_tesis, tab_declaraciones = st.tabs(
    ["General", "Solicitudes", "Sentencias", "Tesis", "Declaraciones"]
)

# GENERAL TAB
with tab_general:
    st.header("General")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total tesis", total_tesis)

    with col2:
        st.metric("Total sentencias", total_sentencias)

    st.subheader("Tesis timeline")
    st.altair_chart(tesis_timeline_chart, use_container_width=True)

    st.subheader("Sentencias timeline")
    st.altair_chart(sentencias_timeline_chart, use_container_width=True)


# SENTENCIAS TAB

with tab_sentencias:
    st.header("Sentencias")

    sub1, sub2, sub3 = st.tabs(["Timeline", "Votaciones", "Ministros"])

    with sub1:
        st.altair_chart(sentencias_timeline_chart, use_container_width=True)

    with sub2:
        st.altair_chart(sentencias_votacion_chart, use_container_width=True)

    with sub3:
        st.altair_chart(sentencias_heatmap, use_container_width=True)


# TESIS TAB

with tab_tesis:
    st.header("Tesis")

    sub1, sub2, sub3, sub4, sub5 = st.tabs(
        ["Timeline", "Materias", "Ministros", "Productividad", "Ngrams"]
    )

    with sub1:
        st.altair_chart(tesis_timeline_chart, use_container_width=True)

    with sub2:
        st.altair_chart(tesis_materias_chart, use_container_width=True)

    with sub3:
        st.altair_chart(tesis_heatmap, use_container_width=True)

    with sub4:
        avg_table, avg_chart = get_productivity_ministros_app()

        st.altair_chart(avg_chart, use_container_width=True)

        selected_year = st.selectbox("Selecciona un año", avg_table["anio"].unique())
        # Filter dataframe
        filtered_df = avg_table[avg_table["anio"] == selected_year]

        # Display table
        st.dataframe(filtered_df, use_container_width=True)

    with sub5:
        render_ngrams_tesis_tab()
