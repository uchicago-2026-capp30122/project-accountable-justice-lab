import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt

BASE_DIR = Path(__file__).parent.parent

TESIS_DATA = BASE_DIR / "data" / "tesis" / "tesis_data"

tesis_complete_path = TESIS_DATA / "tesis_joined_data_full.csv"
tesis_2015_path = TESIS_DATA / "tesis_joined_data_2015.csv"

tesis_complete = pd.read_csv(tesis_complete_path, dtype=str, index_col=0)
tesis_2015 = pd.read_csv(tesis_2015_path, dtype=str, index_col=0)


def return_totals():

    return len(tesis_complete)


def return_materias_chart():
    materias = (
        tesis_complete.groupby(["anio", "main_materia"])["idTesis"]
        .count()
        .to_frame()
        .reset_index()
    )

    chart = (
        alt.Chart(materias)
        .transform_window(
            rank="rank()",
            sort=[alt.SortField("idTesis", order="descending")],
            groupby=["anio"],
        )
        .mark_line(point=True)
        .encode(
            x=alt.X("anio:O", title="Year"),
            y=alt.Y("rank:O", title="Rank"),
            color="main_materia:N",
            tooltip=["anio:N", "main_materia:N", "idTesis:Q", "rank:Q"],
        )
        .properties(width=500, height=500)
    ).interactive()

    return chart
