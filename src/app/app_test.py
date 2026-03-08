## streamlit run src/app/app_test.py

import sys
from pathlib import Path

# Allow imports from src/
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd

from analysis.declaraciones.declaraciones_viz_educ import build_edu_table
from analysis.declaraciones.declaraciones_viz_inmuebles import build_inmuebles_table
from analysis.declaraciones.declaraciones_viz_salario import build_salary_table


from analysis.tesis.tesis_graphs import (
    get_all_tesis_charts
)

from analysis.sentencias.sentencias_graphs import (
    get_all_sentencias_charts
)

from analysis.solicitudes.viz_solicitudes_2 import render_solicitudes_tab

# PAGE CONFIG
st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.title("⚖️ OJO PIOJO")
st.write("Accountable Justice Lab")
##st.image("frontend/ojopiojo.jpeg", width=120)


# DATA PATHS
DECLARACIONES_INMUEBLES_XLSX = "data/clean_data/declaraciones/total_inmuebles.xlsx"
DECLARACIONES_XLSX = "data/clean_data/declaraciones/final_variables.xlsx"
SOLICITUDES_COUNTS_CSV = "data/viz_data/todos_los_ministros_timeseries.csv"

# DATA LOADERS

@st.cache_data
def load_declaraciones():
    return pd.read_excel(
        DECLARACIONES_XLSX,
        engine="openpyxl"
    )

@st.cache_data
def load_declaraciones_inmuebles():
    return pd.read_excel(
        DECLARACIONES_INMUEBLES_XLSX,
        engine="openpyxl"
    )

@st.cache_data
def load_solicitudes_counts():
    df = pd.read_csv(SOLICITUDES_COUNTS_CSV)
    df["year"] = df["year"].astype(str)
    return df

def clean_text(text):
    if not isinstance(text, str):
        return text

    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã": "Á",
        "Ã‰": "É",
        "Ã": "Í",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã‘": "Ñ",
        "È": "é",
        "Ì": "í",
        "Ò": "ñ",
        "Û": "ó",
        "Õ": "í",
        "·": "á",
        "®": "í",
        "ÔøΩ": "í",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text

declaraciones = load_declaraciones()
declaraciones_inmuebles = load_declaraciones_inmuebles()
solicitudes_counts = load_solicitudes_counts()
total_tesis, tesis_timeline_chart, tesis_materias_chart, tesis_heatmap = get_all_tesis_charts()
total_sentencias,sentencias_timeline_chart,sentencias_votacion_chart, sentencias_heatmap = get_all_sentencias_charts ()

for col in declaraciones.select_dtypes(include="object").columns:
    declaraciones[col] = declaraciones[col].apply(clean_text)

for col in declaraciones_inmuebles.select_dtypes(include="object").columns:
    declaraciones_inmuebles[col] = declaraciones_inmuebles[col].apply(clean_text)
    
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
        st.altair_chart(sentencias_timeline_chart, use_container_width=True)

    with sub2:
        st.altair_chart(sentencias_votacion_chart, use_container_width=True)

    with sub3:
        st.altair_chart(sentencias_heatmap, use_container_width=True)


# TESIS TAB

with tab_tesis:

    st.header("Tesis")

    sub1, sub2, sub3 = st.tabs(
        ["Timeline", "Materias", "Ministros"]
    )

    with sub1:
        st.altair_chart(tesis_timeline_chart, use_container_width=True)

    with sub2:
        st.altair_chart(tesis_materias_chart, use_container_width=True)

    with sub3:
        st.altair_chart(tesis_heatmap, use_container_width=True)


# DECLARACIONES TAB

with tab_declaraciones:

    st.header("Declaraciones")

    sub1, sub2, sub3 = st.tabs(
        ["Nivel educativo", "Bienes inmuebles", "Salarios"]
    )

    with sub1:
        st.subheader("Nivel educativo más alto declarado por persona")
        edu_table = build_edu_table(declaraciones)
        st.dataframe(edu_table, use_container_width=True, hide_index=True)

    with sub2:
        st.subheader("Bienes inmuebles")
        inmuebles_table = build_inmuebles_table(declaraciones_inmuebles)
        st.dataframe(inmuebles_table, use_container_width=True,hide_index=True)

    with sub3:
        st.subheader("Salario declarado")
        salary_table = build_salary_table(declaraciones)
        st.dataframe(salary_table, use_container_width=True, hide_index=True)