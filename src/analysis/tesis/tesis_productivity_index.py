import altair as alt
import csv
import numpy as np
import pandas as pd
import re
from pathlib import Path
from datetime import datetime as dt


BASE_DIR = Path(__file__).resolve().parents[3]

SENTENCIAS_DATA = BASE_DIR / "data" / "clean_data" / "sentencias_data"
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

sentencias_data = SENTENCIAS_DATA / "sentencias_joined_data.csv"
tesis_data = TESIS_DATA / "tesis_joined_data_scjn.csv"


def generate_productivity_index_table(sentencias, tesis):
    """
    Return productivity index per justice

    """

    sentencias_ministro = (
        sentencias.groupby(["anio", "ministro"])["expediente"]
        .count()
        .to_frame()
        .reset_index()
    )
    tesis_ministro = (
        tesis.groupby(["anio", "ministro"])["idTesis"].count().to_frame().reset_index()
    )

    prod_ministros = pd.merge(
        tesis_ministro, sentencias_ministro, on=["anio", "ministro"], how="outer"
    )
    prod_ministros = prod_ministros.fillna(0)
    prod_ministros["productividad"] = np.where(
        prod_ministros["expediente"] > 0,
        prod_ministros["idTesis"] / prod_ministros["expediente"],
        np.nan,
    )

    return prod_ministros


def return_productivity_table_chart(ministros):

    avg_by_year = (
        ministros.groupby("anio")["productividad"]
        .mean()
        .fillna(0)
        .to_frame()
        .reset_index()
    )

    productivity_chart = (
        alt.Chart(avg_by_year)
        .mark_line(point=True)
        .transform_filter("datum.anio != 2026")
        .encode(
            x=alt.X("anio:O", title="Año (Year)"),
            y=alt.Y(
                "productividad:Q", title="Índice de productividad (productivity index)"
            ),
            tooltip=[
                alt.Tooltip("anio:O", title="Año (Year)"),
                alt.Tooltip("productividad:Q", title="Índice (Index)", format="%"),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text="Índice de productividad (tesis sobre sentencias)",
                subtitle="Productivity index (tesis over rulings)",
            ),
            height=250,
        )
        .configure_axis(grid=False)
    )

    return avg_by_year, productivity_chart


def get_productivity_ministros_app():

    sentencias = pd.read_csv(sentencias_data, dtype=str)
    sentencias_2015 = sentencias[sentencias["anio"].astype("Int64") >= 2015]
    tesis = sentencias[sentencias["anio"].astype("Int64") >= 2015]
    tesis_2015 = tesis[tesis["anio"].astype("Int64") >= 2015]

    prod_ministros = generate_productivity_index_table(sentencias_2015, tesis_2015)
    avg_prod_table, avg_prod_chart = return_productivity_table_chart(prod_ministros)

    return avg_prod_table, avg_prod_chart
