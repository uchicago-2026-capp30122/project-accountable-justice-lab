import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

BASE_DIR = Path(__file__).parent.parent

SENTENCIAS_DATA = BASE_DIR / "data" / "sentencias" / "sentencias_data"

sentencias_complete_path = SENTENCIAS_DATA / "sentencias_joined_data_full.csv"
sentencias_2015_path = SENTENCIAS_DATA / "sentencias_joined_data_2015.csv"


sentencias_complete = pd.read_csv(sentencias_complete_path, dtype=str)
sentencias_2015 = pd.read_csv(sentencias_2015_path, dtype=str)


def return_totals():

    return len(sentencias_complete)


def return_materias_chart():

    counts_sentencias = (
        sentencias_complete.groupby("anio", "mes")["expediente"]
        .count()
        .to_frame()
        .reset_index()
    )

    return chart


def return_votacion_percentages():

    counts_sentencias = (
        sentencias_complete.groupby(["anio", "votos"])["expediente"]
        .count()
        .to_frame()
        .reset_index()
    )
    counts_sentencias["percentage"] = (
        counts_sentencias["expediente"]
        / counts_sentencias.groupby("anio")["expediente"].transform("sum")
    ) * 100

    chart_sentencias = (
        alt.Chart(counts_sentencias)
        .mark_bar(point=True)
        .encode(
            x=alt.X("anio:O", title="Year"),
            y=alt.Y("percentage:Q", title="Number of rulings"),
            color=alt.Color("votos:N", title="Vote type"),
            tooltip=["anio", "votos", "percentage:Q"],
        )
    )

    return chart_sentencias
