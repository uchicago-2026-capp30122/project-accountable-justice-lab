import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

BASE_DIR = Path(__file__).parent.parent.parent.parent

SENTENCIAS_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"

sentencias_data = SENTENCIAS_DATA / "sentencias_joined_data.csv"


def return_dfs():
    """
    Returns total sentencias
    """
    sentencias_pd = pd.read_csv(sentencias_data, dtype=str)
    sentencias_2015 = sentencias_pd[sentencias_pd["anio"].astype("Int64") >= 2015]

    return sentencias_pd, sentencias_2015


def return_totals(sentencias_pd):
    """
    Returns total sentencias
    """

    return len(sentencias_pd)


sentencias, sentencias_2015 = return_dfs()


def sentencias_timeline():
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
            x=alt.X("anio:T", title="Año"),
            y=alt.Y("expediente:Q", title="Sentencias"),
            tooltip=[
                alt.Tooltip("anio:T", title="Año"),
                alt.Tooltip("expediente:Q", title="Sentencias emitidas"),
            ],
        )
        .properties(
            title=alt.Title("Sentencias emitidas a lo largo del tiempo"),
            width=800,
            height=500,
        )
        .configure_title(fontSize=15)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#eeeeee")
    )

    return chart_timeline


def return_votacion_percentages():
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
            x=alt.X("anio:O", title="Año"),
            y=alt.Y("percentage:Q", title="Total de sentencias"),
            color=alt.Color("votos:N", title="Tipo votación"),
            tooltip=[
                alt.Tooltip("anio", title="año"),
                alt.Tooltip("votos", title="tipo votación"),
                alt.Tooltip("percentage:Q", title="porcentaje", format=".2%"),
            ],
        )
        .properties(
            title=alt.Title(
                "Proporción de votación en las sentencias",
                subtitle="Entendiendo la integridad de los datos",
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


def return_ministros_chart():
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
                alt.Tooltip("anio:N", title="Año"),
                alt.Tooltip("ministro:N", title="Ministra/o"),
                alt.Tooltip("expediente:Q", title="Sentencias emitidas"),
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

    return chart_ministro
