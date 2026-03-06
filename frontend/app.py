import streamlit as st
import pandas as pd
import altair as alt

st.title("Ojo Piojo ;)")
st.write("Accountable Justice Lab")
st.image("frontend/ojopiojo.jpeg", width=100)

# Leer datos
tesis = pd.read_csv("frontend/tesis_joined_data.csv", dtype=str, index_col=0)
sentencias = pd.read_csv("frontend/sentencias_joined_data.csv", dtype=str, index_col=0)
df = pd.read_excel("frontend/declaraciones/final_variables.xlsx")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["General", "Judges", "Declarations"])


def return_materias_chart():
    materias = (
        tesis.groupby(["anio", "main_materia"])["idTesis"]
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


with tab1:
    st.header("General")
    chart = return_materias_chart()
    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.header("Judges")
    st.write("Aquí irán las visualizaciones de sentencias.")

with tab3:
    st.header("Declarations")

    edu_por_persona = (
        df.groupby(["nombre", "primer_apellido", "segundo_apellido"])[
            "edu_highest_level"
        ]
        .first()
        .reset_index()
    )

    edu_por_persona = edu_por_persona.rename(
        columns={
            "nombre": "Nombre",
            "primer_apellido": "Primer apellido",
            "segundo_apellido": "Segundo apellido",
            "edu_highest_level": "Nivel educativo",
        }
    )

    st.subheader("Nivel educativo por persona")
    st.dataframe(edu_por_persona, use_container_width=True)
