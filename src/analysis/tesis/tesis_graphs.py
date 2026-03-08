import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt


BASE_DIR = Path(__file__).parent.parent.parent.parent

SENTENCIAS_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

sentencias = SENTENCIAS_DATA / "sentencias_joined_data.csv"
tesis_data = TESIS_DATA / "tesis_joined_data_scjn.csv"


def return_dfs():
    """
    Returns total tesis
    """
    tesis_pd = pd.read_csv(tesis_data, dtype=str)
    tesis_2015 = tesis_pd[tesis_pd["anio"].astype("Int64") >= 2015]

    return tesis_pd, tesis_2015


def return_totals_tesis(tesis):
    """
    Returns total tesis
    """

    return len(tesis)


def return_tesis_timeline(tesis):
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


def return_tesis_por_tipo_chart(tesis):
    tesis_2025 = tesis[
        (tesis["anio"].astype("Int64") >= 2010)
        & (tesis["anio"].astype("Int64") <= 2025)
    ]
    tesis_2026 = tesis[(tesis["anio"].astype("Int64") >= 2026)]
    counts_tesis_tipo_2025 = (
        tesis_2025.groupby(["anio", "tipoTesis"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )
    counts_tesis_tipo_2026 = (
        tesis_2026.groupby(["anio", "tipoTesis"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    area_tipo_2025 = (
        alt.Chart(counts_tesis_tipo_2025)
        .mark_area(opacity=0.5)
        .encode(
            x=alt.X("anio:O", title="Año"),
            y=alt.Y("idTesis:Q", stack=True, title="Tesis emitidas"),
            color=alt.Color(
                "tipoTesis:N",
                legend=alt.Legend(
                    orient="right", title="Tipo de tesis", labelFontSize=10
                ),
                title="Tipo de tesis",
                scale=alt.Scale(range=["#08283a", "#2D7CC6"]),
            ),
            order=alt.Order("tipoTesis:N"),
            tooltip=[
                alt.Tooltip("anio:O", title="Año"),
                alt.Tooltip("tipoTesis:N", title="Tipo"),
                alt.Tooltip("idTesis:Q", title="Tesis emitidas", format=","),
            ],
        )
    )

    point_tipo_2026 = (
        alt.Chart(counts_tesis_tipo_2026)
        .transform_filter("datum.anio >= 2010")
        .transform_stack(
            stack="idTesis",
            as_=["y0", "y1"],
            groupby=["anio"],
            sort=[alt.SortField("tipoTesis")],
        )
        .mark_point(size=140, filled=True, stroke="white", strokeWidth=1.5)
        .encode(
            x=alt.X("anio:O"),
            y=alt.Y("idTesis:Q"),
            color=alt.Color("tipoTesis:N", legend=None),
            tooltip=[
                alt.Tooltip("anio:O", title="Año"),
                alt.Tooltip("tipoTesis:N", title="Tipo"),
                alt.Tooltip("idTesis:Q", title="Tesis emitidas", format=","),
            ],
        )
    )

    chart_tesis_por_tipo = (
        (area_tipo_2025 + point_tipo_2026)
        .properties(
            title=alt.Title(
                "Tesis emitidas por la SCJN a lo largo del tiempo por tipo"
            ),
            width=800,
            height=500,
            padding={"left": 50, "right": 100, "top": 50, "bottom": 10},
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_tesis_por_tipo


def return_tesis_materias_chart(tesis_2015):
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


def return_tesis_heatmap(tesis_2015):

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

    return chart_tesis_ministro


def get_all_tesis_charts():

    tesis, tesis_2015 = return_dfs()

    total_tesis = return_totals_tesis(tesis)
    tesis_timeline_chart = return_tesis_timeline(tesis)
    tesis_por_tipo_chart = return_tesis_por_tipo_chart()
    tesis_materias_chart = return_tesis_materias_chart(tesis_2015)
    tesis_heatmap = return_tesis_heatmap(tesis_2015)

    return (
        total_tesis,
        tesis_timeline_chart,
        tesis_por_tipo_chart,
        tesis_materias_chart,
        tesis_heatmap,
    )
