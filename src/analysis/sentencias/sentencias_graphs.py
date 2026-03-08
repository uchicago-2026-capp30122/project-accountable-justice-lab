import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

BASE_DIR = Path(__file__).resolve().parents[3]

SENTENCIAS_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"

sentencias_data = SENTENCIAS_DATA / "sentencias_joined_data.csv"


def return_totals_sentencias(sentencias):
    """
    Returns total sentencias
    """

    return len(sentencias)


def return_sentencias_timeline(sentencias):
    """
    Returns timeline of sentencias over time

    """
    counts_sentencias = (
        sentencias.groupby("anio")["expediente"].count().to_frame().reset_index()
    )

    chart_timeline = (
        alt.Chart(counts_sentencias)
        .mark_line(point=True, color="#2b6cb0")
        .encode(
            x=alt.X("anio:T", title="Año (Year)"),
            y=alt.Y("expediente:Q", title="Sentencias (Rulings)"),
            tooltip=[
                alt.Tooltip("anio:T", title="Año"),
                alt.Tooltip(
                    "expediente:Q", title="Sentencias emitidas (Emitted rulings)"
                ),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Sentencias emitidas por la SCJN (totales)",
                subtitle="Emitted rulings by the Supreme Court (totals)",
            ),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_timeline


def return_votacion_percentages(sentencias):
    """

    Returns bar graph sentencias

    """

    counts_sentencias = (
        sentencias.groupby(["anio", "votos"])["expediente"]
        .count()
        .to_frame()
        .reset_index()
    )
    counts_sentencias["percentage"] = counts_sentencias[
        "expediente"
    ] / counts_sentencias.groupby("anio")["expediente"].transform("sum")

    votacion_sentencias = (
        alt.Chart(counts_sentencias)
        .mark_bar(point=True)
        .encode(
            x=alt.X("anio:O", title="Año (Year)"),
            y=alt.Y("percentage:Q", title="Sentencias (Rulings)"),
            color=alt.Color("votos:N", title="Tipo votación (kind of vote)"),
            tooltip=[
                alt.Tooltip("anio", title="Año (Year)"),
                alt.Tooltip("votos", title="Tipo votación (kind of vote)"),
                alt.Tooltip(
                    "percentage:Q", title="Porcentaje (percentage)", format=".2%"
                ),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Proporción de votación en las sentencias",
                subtitle=[
                    "Entendiendo la integridad de los datos",
                    "Voting proportions in rulings (understanding data integrity)",
                ],
            ),
            width=500,
            height=300,
        )
        .configure_title(
            fontSize=15,
        )
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return votacion_sentencias


def return_heatmap_sentencias(sentencias_2015):
    """
    Returns heat map ministros

    """
    sentencias_ministro = (
        sentencias_2015.groupby(["anio", "ministro"])["expediente"]
        .count()
        .to_frame()
        .reset_index()
    )

    chart_ministro = (
        alt.Chart(sentencias_ministro)
        .mark_rect()
        .encode(
            x="anio:O",
            y=alt.Y("ministro:N", sort="-x"),
            color=alt.Color("expediente:Q", title="Rulings"),
            tooltip=[
                alt.Tooltip("anio:N", title="Año (Year)"),
                alt.Tooltip("ministro:N", title="Ministra/o (Justice)"),
                alt.Tooltip(
                    "expediente:Q", title="Sentencias emitidas (Emitted rulings)"
                ),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Sentencias emitidas por ministra/o",
                subtitle="Emitted rulings by justice",
            ),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_ministro


def get_all_sentencias_charts():

    sentencias = pd.read_csv(sentencias_data, dtype=str)
    sentencias_2015 = sentencias[sentencias["anio"].astype("Int64") >= 2015]

    total_sentencias = return_totals_sentencias(sentencias)
    sentencias_timeline_chart = return_sentencias_timeline(sentencias)
    sentencias_votacion_chart = return_votacion_percentages(sentencias)
    sentencias_heatmap = return_heatmap_sentencias(sentencias_2015)

    return (
        total_sentencias,
        sentencias_timeline_chart,
        sentencias_votacion_chart,
        sentencias_heatmap,
    )
