## streamlit run src/app/app_test.py

import sys
from pathlib import Path

# Allow imports from src/
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd

from analysis.declaraciones.declaraciones_viz_educ import build_edu_table
from analysis.declaraciones.declaraciones_viz_inmuebles import build_inmuebles_table

from analysis.sentencias.sentencias_graphs import (
    return_totals as sentencias_total,
    sentencias_timeline,
    return_votacion_percentages,
    return_ministros_chart,
)

from analysis.tesis.tesis_graphs import (
    return_totals as tesis_total,
    tesis_timeline,
    return_materias_chart,
    return_heatmap_tesis,
)

from analysis.solicitudes.viz_solicitudes_2 import render_solicitudes_tab

# PAGE CONFIG
st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.title("⚖️ OJO PIOJO")
st.write("Accountable Justice Lab")
##st.image("frontend/ojopiojo.jpeg", width=120)


# DATA PATHS

DECLARACIONES_XLSX = "data/clean_data/declaraciones/final_variables.xlsx"
SOLICITUDES_COUNTS_CSV = "data/viz_data/todos_los_ministros_timeseries.csv"

# DATA LOADERS
@st.cache_data
def load_declaraciones():
    return pd.read_excel(DECLARACIONES_XLSX)


@st.cache_data
def load_solicitudes_counts():
    df = pd.read_csv(SOLICITUDES_COUNTS_CSV)
    df["year"] = df["year"].astype(str)
    return df


declaraciones = load_declaraciones()
solicitudes_counts = load_solicitudes_counts()

# MAIN TABS


tab_general, tab_solicitudes, tab_sentencias, tab_tesis, tab_declaraciones = st.tabs(
    ["General", "Solicitudes", "Sentencias", "Tesis", "Declaraciones"]
)

# GENERAL TAB
with tab_general:

    st.header("General")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total tesis", tesis_total())

    with col2:
        st.metric("Total sentencias", sentencias_total())

    st.subheader("Tesis timeline")
    st.altair_chart(tesis_timeline(), use_container_width=True)

    st.subheader("Sentencias timeline")
    st.altair_chart(sentencias_timeline(), use_container_width=True)


# SOLICITUDES TAB

with tab_solicitudes:

    render_solicitudes_tab(solicitudes_counts)

# SENTENCIAS TAB

with tab_sentencias:

    st.header("Sentencias")

    sub1, sub2, sub3 = st.tabs(
        ["Timeline", "Votaciones", "Ministros"]
    )

    with sub1:
        st.altair_chart(sentencias_timeline(), use_container_width=True)

    with sub2:
        st.altair_chart(return_votacion_percentages(), use_container_width=True)

    with sub3:
        st.altair_chart(return_ministros_chart(), use_container_width=True)


# TESIS TAB

with tab_tesis:

    st.header("Tesis")

    sub1, sub2, sub3 = st.tabs(
        ["Timeline", "Materias", "Ministros"]
    )

    with sub1:
        st.altair_chart(tesis_timeline(), use_container_width=True)

    with sub2:
        st.altair_chart(return_materias_chart(), use_container_width=True)

    with sub3:
        st.altair_chart(return_heatmap_tesis(), use_container_width=True)


# DECLARACIONES TAB

with tab_declaraciones:

    st.header("Declaraciones")

    sub1, sub2 = st.tabs(
        ["Nivel educativo", "Bienes inmuebles"]
    )

    with sub1:
        st.subheader("Nivel educativo por persona")
        edu_table = build_edu_table(declaraciones)
        st.dataframe(edu_table, use_container_width=True)

    with sub2:
        st.subheader("Bienes inmuebles")
        inmuebles_table = build_inmuebles_table(declaraciones)
        st.dataframe(inmuebles_table, use_container_width=True)