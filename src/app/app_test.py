import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from viz_solicitudes_test import render_solicitudes_tab
from table_declaraciones import render_declaraciones_tab

# Page configuration
st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.title("⚖️ OJO PIOJO")
st.write("Accountable Justice Lab")
##st.image("frontend/ojopiojo.jpeg", width=100)

# File paths
SOLICITUDES_COUNTS_CSV = "todos_los_ministros_timeseries.csv"
TESIS_CSV = "frontend/tesis_joined_data.csv"
SENTENCIAS_CSV = "frontend/sentencias_joined_data.csv"
DECLARACIONES_XLSX = "frontend/declaraciones/final_variables.xlsx"


@st.cache_data
def load_main_data():
    """Load all dashboard datasets only once."""
    tesis = pd.read_csv(TESIS_CSV, dtype=str, index_col=0)
    sentencias = pd.read_csv(SENTENCIAS_CSV, dtype=str, index_col=0)
    declaraciones = pd.read_excel(DECLARACIONES_XLSX)
    solicitudes_counts = pd.read_csv(SOLICITUDES_COUNTS_CSV)

    solicitudes_counts["year"] = solicitudes_counts["year"].astype(str)

    return tesis, sentencias, declaraciones, solicitudes_counts


def return_materias_chart(tesis_df):
    """
    Build the tesis chart showing the ranking of main topics by year.
    """
    materias = (
        tesis_df.groupby(["anio", "main_materia"])["idTesis"]
        .count()
        .reset_index(name="n_tesis")
    )

    chart = (
        alt.Chart(materias)
        .transform_window(
            rank="rank()",
            sort=[alt.SortField("n_tesis", order="descending")],
            groupby=["anio"],
        )
        .mark_line(point=True)
        .encode(
            x=alt.X("anio:O", title="Year"),
            y=alt.Y("rank:O", title="Rank"),
            color="main_materia:N",
            tooltip=["anio:N", "main_materia:N", "n_tesis:Q", "rank:Q"],
        )
        .properties(width=500, height=500)
        .interactive()
    )

    return chart


tesis, sentencias, declaraciones, solicitudes_counts = load_main_data()

# Main tabs
tab_general, tab_solicitudes, tab_sentencias, tab_tesis, tab_declaraciones = st.tabs(
    ["General", "Solicitudes", "Sentencias", "Tesis", "Declaraciones"]
)

with tab_general:
    st.header("General")
    chart_general = return_materias_chart(tesis)
    st.altair_chart(chart_general, use_container_width=True)

with tab_solicitudes:
    render_solicitudes_tab(solicitudes_counts)

with tab_sentencias:
    st.header("Sentencias")
    st.write("Here you can add the visualizations for sentencias.")

with tab_tesis:
    st.header("Tesis")
    st.write("Here you can add the visualizations for tesis.")

with tab_declaraciones:
    render_declaraciones_tab(declaraciones)