import streamlit as st


st.title("Ojo Piojo ;)")
st.write("Accountable Justice Lab")
st.image("frontend/ojopiojo.jpeg", width=100)

import pandas as pd
import altair as alt


tesis = pd.read_csv("frontend/tesis_joined_data.csv", dtype=str, index_col=0)
sentencias = pd.read_csv("frontend/sentencias_joined_data.csv", dtype=str, index_col=0)


def return_materias_chart():
    materias = (
        tesis.groupby(["anio", "main_materia"])["idTesis"]
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

chart = return_materias_chart()
st.altair_chart(chart, use_container_width=True)