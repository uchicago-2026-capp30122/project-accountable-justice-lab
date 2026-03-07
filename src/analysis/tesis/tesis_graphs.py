import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt


BASE_DIR = Path(__file__).parent.parent
SENTENCIAS_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

sentencias = SENTENCIAS_DATA / "sentencias_joined_data.csv"
tesis_data = TESIS_DATA / "tesis_joined_data_scjn.csv"

tesis = pd.read_csv(tesis_data, dtype=str)
tesis_2015 = tesis[tesis["anio"].astype("Int64") >= 2015]


def return_totals():
    """
    Returns total tesis
    """

    return len(tesis)


def tesis_timeline():
    """
    Returns timeline of tesis
    """
    counts_tesis = tesis.groupby("anio")["idTesis"].count().to_frame().reset_index()

    chart_timeline = (
        alt.Chart(counts_tesis)
        .mark_line(point=True, color="#2b6cb0")
        .encode(
            x=alt.X("anio:T", title="Año"),
            y=alt.Y("idTesis:Q", title="Tesis"),
            tooltip=[
                alt.Tooltip("anio:T", title="Año", format="%Y"),
                alt.Tooltip("idTesis:Q", title="Sentencias emitidas", format=","),
            ],
        )
        .properties(
            title=alt.Title("Tesis emitidas por la SCJN a lo largo del tiempo"),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_timeline


def return_materias_chart():
    materias = (
        tesis_2015.groupby(["anio", "main_materia"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    chart_materias = (
        alt.Chart(materias)
        .transform_window(
            rank="rank()",
            sort=[alt.SortField("idTesis", order="descending")],
            groupby=["anio"],
        )
        .mark_line(point=alt.OverlayMarkDef(size=70))
        .encode(
            x=alt.X("anio:T", title="Año"),
            y=alt.Y("rank:Q", title="Ranking", scale=alt.Scale(reverse=True)),
            color=alt.Color(
                "main_materia:N",
                legend=alt.Legend(title="Materias", symbolSize=50, labelFontSize=10),
            ),
            tooltip=[
                alt.Tooltip("anio:T", title="Año", format="%Y"),
                alt.Tooltip("main_materia:N", title="Materia"),
                alt.Tooltip("idTesis:Q", title="Número de tesis"),
                alt.Tooltip("rank:Q", title="Ranking materia"),
            ],
        )
        .properties(
            title=alt.Title("Ranking de materias por año"),
            width=650,
            height=400,
            padding={"left": 50, "right": 100, "top": 50, "bottom": 10},
        )
        .configure_axis(grid=False)
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
    )

    return chart_materias


def return_heatmap_tesis():

    tesis_ministro = (
        tesis_2015.groupby(["anio", "ministro"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    chart_tesis_ministro = (
        alt.Chart(tesis_ministro)
        .mark_rect()
        .encode(
            x="anio:O",
            y=alt.Y("ministro:N", sort="-x"),
            color=alt.Color("idTesis:Q", title="Tesis"),
            tooltip=[
                alt.Tooltip("anio:N", title="Año"),
                alt.Tooltip("ministro:N", title="Ministra/o"),
                alt.Tooltip("idTesis:Q", title="Sentencias emitidas"),
            ],
        )
        .properties(
            title=alt.Title("Sentencias emitidas por ministra/o a lo largo del tiempo"),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    chart_tesis_ministro
