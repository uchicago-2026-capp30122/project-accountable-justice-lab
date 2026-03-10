import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

"""

This file contains all of the functions necessary to create the graphs for the 
Tesis tab of the app. 

"""


BASE_DIR = Path(__file__).resolve().parents[3]

TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

tesis_data = TESIS_DATA / "tesis_joined_data_scjn.csv"


def return_totals_tesis(tesis):
    """

    This function returns total tesis emitted.

    Inputs:
        tesis (df): dataframe of historical tesis emitted.

    Returns:
        len(tesis) (int): total number of tesis emitted
    """

    return len(tesis)


def return_tesis_timeline(tesis):
    """

    This function returns a timeline of total tesis emitted by year.

    Inputs:
        tesis (df): dataframe of historical tesis emitted.

    Returns:
        chart_timeline (chart): "mark_line" type chart that displays a
            line graph of tesis over the years

    """
    counts_tesis = tesis.groupby("anio")["idTesis"].count().to_frame().reset_index()
    counts_tesis["anio"] = pd.to_datetime(counts_tesis["anio"], format="%Y")

    chart_timeline = (
        alt.Chart(counts_tesis)
        .mark_line(point=True, color="#255487")
        .encode(
            x=alt.X("anio:T", title="Año (Year)"),
            y=alt.Y("idTesis:Q", title="Tesis"),
            tooltip=[
                alt.Tooltip("anio:T", title="Año (Year)", format="%Y"),
                alt.Tooltip(
                    "idTesis:Q", title="Tesis emitidas (Emitted Tesis)", format=","
                ),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Tesis emitidas por la SCJN (totales)",
                subtitle="Emitted tesis by the Supreme Court (totals)",
            ),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_timeline


def return_tesis_por_tipo_chart(tesis):
    """

    This function filters a dataframe, grouping by type of tesis and year, getting
    the total tesis emitted by type. The resulting graph is an area graph
    that maps the number of tesis aisladas and jurisprudencias over the years.

    To avoid a steep reduction in 2026, we added this data value as a point
    rather than a line.

    Inputs:
        tesis (df): dataframe of historical tesis emitted.

    Returns:
        chart_tesis_por_tipo (chart): "mark_area" type chart that displays a
            ranking of areas over the years and a point line corresponding to
            2026.

    """
    # Create filtered dataframe until 2025
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
    # Create filtered dataframe for 2026
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
            x=alt.X("anio:O", title="Año (Year)"),
            y=alt.Y("idTesis:Q", stack=True, title="Tesis emitidas (Emitted Tesis)"),
            color=alt.Color(
                "tipoTesis:N",
                legend=alt.Legend(
                    orient="right",
                    title="Tipo de tesis (Type of Tesis)",
                    labelFontSize=10,
                ),
                title="Tipo de tesis",
                scale=alt.Scale(range=["#08283a", "#2D7CC6"]),
            ),
            order=alt.Order("tipoTesis:N"),
            tooltip=[
                alt.Tooltip("anio:O", title="Año (Year)"),
                alt.Tooltip("tipoTesis:N", title="Tipo (Type)"),
                alt.Tooltip(
                    "idTesis:Q", title="Tesis emitidas (Emitted Tesis)", format=","
                ),
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
                alt.Tooltip("anio:O", title="Año (Year)"),
                alt.Tooltip("tipoTesis:N", title="Tipo (Type)"),
                alt.Tooltip(
                    "idTesis:Q", title="Tesis emitidas (Emitted Tesis)", format=","
                ),
            ],
        )
    )

    chart_tesis_por_tipo = (
        (area_tipo_2025 + point_tipo_2026)
        .properties(
            title=alt.TitleParams(
                text="Tesis emitidas por la SCJN (por tipo)",
                subtitle="Emitted tesis by the Supreme Court (by type)",
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
    """

    This function filters a dataframe, grouping by main area and year, getting
    the total tesis emitted by area. The resulting graph is a rank line graph
    that maps the ranking of each area over the years.

    Inputs:
        tesis_2025 (df): dataframe of tesis emitted from 2015 to date.

    Returns:
        chart_materias (chart): "transform_window" type chart that displays a
            ranking of areas over the years.

    """
    # Create filtered dataframe
    materias = (
        tesis_2015.groupby(["anio", "main_materia"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    # Convert "anio" to a year datatype
    materias["anio"] = pd.to_datetime(materias["anio"], format="%Y")

    chart_materias = (
        alt.Chart(materias)
        .transform_window(
            rank="rank()",
            sort=[alt.SortField("idTesis", order="descending")],
            groupby=["anio"],
        )
        .mark_line(point=alt.OverlayMarkDef(size=70))
        .encode(
            x=alt.X("anio:T", title="Año (Year)"),
            y=alt.Y("rank:Q", title="Ranking", scale=alt.Scale(reverse=True)),
            color=alt.Color(
                "main_materia:N",
                legend=alt.Legend(
                    title="Materias (Areas)", symbolSize=50, labelFontSize=10
                ),
            ),
            tooltip=[
                alt.Tooltip("anio:T", title="Año (Year)", format="%Y"),
                alt.Tooltip("main_materia:N", title="Materia (Area)"),
                alt.Tooltip("idTesis:Q", title="Número de tesis (Number of Tesis)"),
                alt.Tooltip("rank:Q", title="Ranking materia (Area ranking)"),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Ranking de materias por año",
                subtitle="Area ranking by year",
            ),
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
    """

    This function filters a dataframe, grouping by justice and year, getting
    the total tesis emitted by each justice. The resulting graph is a heatmap
    that links total tesis per justice over time.

    Inputs:
        tesis_2015 (df): dataframe of tesis emitted from 2015 to date.

    Returns:
        chart_tesis_ministro (chart): "mark_rect" type chart that displays a
            heatmap.

    """
    # Create filtered dataframe
    tesis_ministro = (
        tesis_2015.groupby(["anio", "ministro"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    # Create chart
    chart_tesis_ministro = (
        alt.Chart(tesis_ministro)
        .mark_rect()
        .encode(
            x=alt.X("anio:O", title="Año (Year)"),
            y=alt.Y("ministro:N", sort="-x"),
            color=alt.Color("idTesis:Q", title="Tesis"),
            tooltip=[
                alt.Tooltip("anio:N", title="Año (Year)"),
                alt.Tooltip("ministro:N", title="Ministra/o (Justice)"),
                alt.Tooltip("idTesis:Q", title="Tesis emitidas (Emitted rulings)"),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Tesis emitidas por ministra/o",
                subtitle="Emitted tesis by justice",
            ),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_tesis_ministro


def get_all_tesis_charts():
    """
    Function that returns all charts related to tesis, using as default the
    tesis dataframe, which will be filtered for 2015 as default for certain
    graphs that require a smaller range of values for years.

    Returns:
        - total_tesis (int): total tesis contained in database
        - tesis_timeline_chart (alt chart): chart containing total tesis over the
            years
        - tesis_por_tipo_chart (alt chart): chart containing tesis per type
        - tesis_materias_chart (alt chart): chart containing rank line of areas
        - tesis_heatmap (alt chart): chart containing tesis by justice

    """

    tesis = pd.read_csv(tesis_data, dtype=str)
    tesis_2015 = tesis[tesis["anio"].astype("Int64") >= 2015]

    total_tesis = return_totals_tesis(tesis)
    tesis_timeline_chart = return_tesis_timeline(tesis)
    tesis_por_tipo_chart = return_tesis_por_tipo_chart(tesis_2015)
    tesis_materias_chart = return_tesis_materias_chart(tesis_2015)
    tesis_heatmap = return_tesis_heatmap(tesis_2015)

    return (
        total_tesis,
        tesis_timeline_chart,
        tesis_por_tipo_chart,
        tesis_materias_chart,
        tesis_heatmap,
    )
