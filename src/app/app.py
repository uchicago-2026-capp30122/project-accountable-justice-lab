## Run final app with: streamlit run src/app/app_test.py

import sys
from pathlib import Path

# Allow imports from src/
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd

# Import table-building functions for the Declaraciones tab
from analysis.declaraciones.declaraciones_viz_educ import build_edu_table
from analysis.declaraciones.declaraciones_viz_inmuebles import build_inmuebles_table
from analysis.declaraciones.declaraciones_viz_salario import build_salary_table

# Import completeness metrics for the General tab
from analysis.declaraciones.metrica_de_completitud import (
    metrica_completitud_educacion,
    metrica_completitud_inmuebles,
)

# Import chart-building functions for Tesis and Sentencias
from analysis.tesis.tesis_graphs import get_all_tesis_charts

from analysis.sentencias.sentencias_graphs import get_all_sentencias_charts

from analysis.tesis.salient_tokens_tesis_viz import render_ngrams_tesis_tab

# Import rendering function for Solicitudes tab
from analysis.solicitudes.viz_solicitudes_2 import render_solicitudes_tab

import streamlit as st

st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.markdown(
    """
<style>
button[data-baseweb="tab"] {
    font-size: 0.95rem;
    font-weight: 500;
    color: #4b5563;
    padding: 0.55rem 1.15rem;
    margin-right: 0.35rem;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #2f3343;
}

div[data-baseweb="tab-list"] {
    gap: 0.65rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# Outer columns to center the whole block
left_space, center, right_space = st.columns([1, 3, 1])

with center:
    title_col, logo_col = st.columns([4, 1])

    with title_col:
        st.markdown(
            """
<h1 style='
    font-size: 90px; 
    margin-bottom: 0px;
    line-height: 1;
    text-align: right;
    font-family:Georgia;
    color:#4682B4;
'>
    OJO PIOJO
</h1>
""",
            unsafe_allow_html=True,
        )

    with logo_col:
        st.image("src/app/ojopiojo.jpeg", width=120)

    st.markdown(
        """
<h2 style='
text-align: center;
font-family:Montserrat;
font-size: 30px;
font-weight: 600;
margin-top: -8px;
margin-bottom: 8px;
color:#2f3343;
'>
    Accountable Justice Lab
</h2>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div style="max-width:1050px; margin:0 auto 24px auto; line-height:1.7;">

<p style="text-align:justify; font-size:15px; color:#374151; margin-bottom:12px;">
<em>Ojo Piojo</em> es una frase chilena que resonó con nosotras; significa estar alerta. 
Queremos empoderar a la ciudadanía mexicana con más herramientas para vigilar y monitorear a las instituciones de su país. 
Esta plataforma es nuestra manera de hacerlo.
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280; margin-top:0;">
<em>Ojo Piojo</em> is a Chilean expression meaning “stay alert.” 
Our goal is to empower Mexican citizens with tools to better observe and monitor public institutions.
This platform is our contribution to that effort.
</p>

</div>
""",
        unsafe_allow_html=True,
    )

# File paths
DECLARACIONES_INMUEBLES_XLSX = "data/clean_data/declaraciones/total_inmuebles.xlsx"
DECLARACIONES_XLSX = "data/clean_data/declaraciones/final_variables.xlsx"
SOLICITUDES_COUNTS_CSV = "data/viz_data/todos_los_ministros_timeseries.csv"
SOLICITUDES_INDEX_CSV = "data/viz_data/noresponse_index_solicitudes.csv"


# Cached data loaders
@st.cache_data
def load_declaraciones():
    return pd.read_excel(DECLARACIONES_XLSX, engine="openpyxl")


@st.cache_data
def load_declaraciones_inmuebles():
    return pd.read_excel(DECLARACIONES_INMUEBLES_XLSX, engine="openpyxl")


@st.cache_data
def load_solicitudes_counts():
    df = pd.read_csv(SOLICITUDES_COUNTS_CSV)
    df["year"] = df["year"].astype(str)
    return df


@st.cache_data
def load_solicitudes_index():
    df = pd.read_csv(SOLICITUDES_INDEX_CSV)
    df["year"] = df["year"].astype(str)
    return df


# Text cleaning helper for encoding issues in declaration files
def clean_text(text):
    if not isinstance(text, str):
        return text

    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã": "Á",
        "Ã‰": "É",
        "Ã": "Í",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã‘": "Ñ",
        "È": "é",
        "Ì": "í",
        "Ò": "ñ",
        "Û": "ó",
        "Õ": "í",
        "·": "á",
        "®": "í",
        "ÔøΩ": "í",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


# Load datasets
declaraciones = load_declaraciones()
declaraciones_inmuebles = load_declaraciones_inmuebles()
solicitudes_counts = load_solicitudes_counts()
solicitudes_index = load_solicitudes_index()

(
    total_tesis,
    tesis_timeline_chart,
    tesis_por_tipo_chart,
    tesis_materias_chart,
    tesis_heatmap,
) = get_all_tesis_charts()
(
    total_sentencias,
    sentencias_timeline_chart,
    sentencias_votacion_chart,
    sentencias_heatmap,
) = get_all_sentencias_charts()

# Clean text columns
for col in declaraciones.select_dtypes(include="object").columns:
    declaraciones[col] = declaraciones[col].apply(clean_text)

for col in declaraciones_inmuebles.select_dtypes(include="object").columns:
    declaraciones_inmuebles[col] = declaraciones_inmuebles[col].apply(clean_text)

# Completeness metrics
m1 = metrica_completitud_educacion(declaraciones)
m2 = metrica_completitud_inmuebles(declaraciones_inmuebles)


# App tabs
(
    tab_about,
    tab_general,
    tab_solicitudes,
    tab_sentencias,
    tab_tesis,
    tab_declaraciones,
) = st.tabs(
    [
        "About",
        "General",
        "Solicitudes (Requests)",
        "Sentencias (Rulings)",
        "Tesis (Precedents)",
        "Declaraciones (Disclosures)",
    ]
)

# About tab
with tab_about:
    st.header("About")

    st.markdown(
        """
<div style="max-width:1050px; margin:0 auto 30px auto; line-height:1.7;">

<p style="text-align:center; font-size:18px; margin-bottom:10px;">
<strong>¿Por qué Ojo Piojo?</strong>
</p>

<p style="text-align:justify; font-size:15px; color:#374151;">
<em>Ojo Piojo</em> es una frase chilena que resonó con nosotras; significa estar alerta. 
Queremos empoderar a la ciudadanía con más herramientas para vigilar y monitorear a las instituciones de su país. 
Esta plataforma es nuestra manera de hacerlo.
</p>

<p style="text-align:justify; font-size:15px; color:#374151;">
Ojo Piojo es una iniciativa que busca brindar mayor publicidad y transparencia a datos relacionados con la
<strong>Suprema Corte de Justicia de la Nación (SCJN)</strong> de México. 
Como equipo, nos dimos cuenta de que la información judicial muchas veces no se encuentra estandarizada 
ni analizada a gran escala, lo que deja interrogantes sobre cómo funciona esta corte y sus integrantes.
</p>

<p style="text-align:justify; font-size:15px; color:#374151;">
En esta página encontrarás cifras y datos generales sobre cuatro elementos clave de la SCJN:
</p>

<p style="text-align:justify; font-size:15px; color:#374151;">
1. Solicitudes de información presentadas por la ciudadanía<br>
2. Sentencias emitidas por la SCJN<br>
3. Tesis (criterios judiciales orientadores) emitidas por la SCJN<br>
4. Declaraciones de situación patrimonial y de intereses de las ministras y ministros
</p>

<p style="text-align:center; font-size:15px; color:#374151;">
¡Te invitamos a explorar!
</p>

<hr style="margin:28px 0; opacity:0.25;">

<p style="text-align:center; font-size:14px; margin-bottom:6px; color:#4b5563;">
<strong>Why Ojo Piojo?</strong>
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280;">
<em>Ojo Piojo</em> is a Chilean expression meaning “stay alert.” 
Our goal is to empower citizens with tools to better observe and monitor public institutions.
This platform is our contribution to that effort.
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280;">
Ojo Piojo is an initiative that promotes transparency and accessibility of data related to the
<strong>Mexican Supreme Court (SCJN)</strong>. We found that judicial information is often not standardized
or analyzed at scale, leaving important questions about how the court and its members operate.
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280;">
This site presents data and metrics on four key aspects of the SCJN:
information requests, rulings, judicial precedents (tesis), and financial disclosures of the justices.
</p>

</div>
""",
        unsafe_allow_html=True,
    )


# General tabls
with tab_general:
    st.header("General")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total tesis (Total precedents)", total_tesis)

    with col2:
        st.metric("Total sentencias (Total rulings)", total_sentencias)

    st.subheader("Línea de tiempo tesis (Tesis timeline)")
    st.altair_chart(tesis_timeline_chart, use_container_width=True)

    st.subheader("Línea de tiempo sentencias (Rulings timeline)")
    st.altair_chart(sentencias_timeline_chart, use_container_width=True)

    st.subheader("Completitud de declaraciones (Disclosure completeness)")

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Ministros con máximo nivel de educación declarado (Judges with declared maximum level of education)",
            f"{m1['con_educacion_declarada']} / {m1['total_ministros']}",
        )
        st.write(f"Porcentaje (Percentage): {m1['porcentaje']:.1%}")

    with col4:
        st.metric(
            "Ministros con al menos un inmueble declarado (Judges with at least one asset declared)",
            f"{m2['con_al_menos_un_inmueble']} / {m2['total_ministros']}",
        )
        st.write(f"Porcentaje (Percentage): {m2['porcentaje']:.1%}")

# Solicitudes tab
with tab_solicitudes:
    render_solicitudes_tab(solicitudes_counts, solicitudes_index)

# Sentencias tab
with tab_sentencias:
    st.header("Sentencias (Rulings)")

    sub0, sub1, sub2 = st.tabs(
        [
            "Overview",
            "Votaciones (Votings)",
            "Totales por Ministra(o) (Total by Justice)",
        ]
    )

    with sub0:
        st.markdown(
            """<div style="max-width:1050px; margin:0 auto 24px auto; line-height:1.75;">

<p style="text-align:center; font-size:20px; font-weight:600; color:#2f3343; margin-bottom:14px;">
Sentencias
</p>

<p style="text-align:justify; font-size:15px; color:#374151; margin-bottom:12px;">
En esta pestaña podrás encontrar gráficas relacionadas con las sentencias dictadas por la Suprema Corte de Justicia.<br><br>

En <strong>“Votaciones”</strong>, podrás identificar los patrones de votación en las sentencias.
Esta gráfica también nos ayuda a entender la integridad de los datos: para información anterior a 2011,
el registro de la votación no era común por lo que para esos casos nuestro proceso identificó la votación
como <strong>“indeterminada”</strong>.<br><br>

En <strong>“Totales por Ministra(o)”</strong>, encontrarás un mapa de calor con las sentencias emitidas
por cada ministra o ministro en el tiempo.<br><br>

El análisis incluye información de 1989 a la fecha.<br><br>

</p>

<hr style="margin:24px 0; opacity:0.20;">

<p style="text-align:center; font-size:15px; font-weight:600; color:#4b5563; margin-bottom:8px;">
Rulings
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280; margin-top:0;">
This section contains visualizations related to rulings issued by the Mexican Supreme Court.<br><br>

In <strong>“Voting Patterns”</strong>, you can identify voting patterns in rulings.
This chart also helps us understand data completeness: for information prior to 2011,
voting records were not commonly published, so in those cases our process classified the vote
as <strong>“undetermined”</strong>.<br><br>

In <strong>“Totals by Justice”</strong>, you will find a heatmap showing rulings issued
by each justice over time.<br><br>

This analysis includes information from 1989 onward.<br><br>

<em>* Note: the SCJN has not published rulings data for 2026.</em>
</p>

</div>""",
            unsafe_allow_html=True,
        )

    with sub1:
        st.altair_chart(sentencias_votacion_chart, use_container_width=True)

    with sub2:
        st.altair_chart(sentencias_heatmap, use_container_width=True)

# Tesis tab
with tab_tesis:
    st.header("Tesis (Precedents)")

    sub0, sub1, sub2, sub3, sub4 = st.tabs(
        [
            "Overview",
            "Materias (Areas)",
            "Totales por Ministra(o) (Total by Justice)",
            "Por tipo (By type)",
            "Temas Principales (N-grams)",
        ]
    )

    with sub0:
        st.markdown(
            """<div style="max-width:1050px; margin:0 auto 24px auto; line-height:1.75;">

<p style="text-align:center; font-size:20px; font-weight:600; color:#2f3343; margin-bottom:14px;">
Tesis
</p>

<p style="text-align:justify; font-size:15px; color:#374151; margin-bottom:12px;">
En esta pestaña podrás encontrar información relacionada con las tesis emitidas por la SCJN.
Las tesis corresponden a criterios judiciales orientadores que contienen contenido jurídico de alta relevancia.<br><br>

En la pestaña <strong>“Materias”</strong>, podrás encontrar el ranking de las materias a lo largo del año.
La materia con ranking 1 se refiere a la materia más común, mientras que el ranking 6 es la materia con menos tesis emitidas.<br><br>

En la pestaña <strong>“Totales por Ministra(o)”</strong>, encontrarás un mapa de calor con las tesis emitidas
por cada ministra o ministro en el tiempo.<br><br>

En la pestaña <strong>“Por tipo”</strong>, encontrarás el total de tesis emitidas por tipo
(aislada o jurisprudencia). A diferencia de las tesis aisladas, las jurisprudencias corresponden
a criterios obligatorios y vinculantes para las cortes inferiores a la SCJN.<br><br>

En la pestaña <strong>“Temas Principales”</strong>, podrás seleccionar los temas más relevantes
contenidos en los rubros de las tesis por época judicial.<br><br>

El análisis incluye información de 2015 a la fecha
(excepto la pestaña de <strong>“Temas Principales”</strong>, que contiene todas las épocas judiciales desde 1910).
</p>

<hr style="margin:24px 0; opacity:0.20;">

<p style="text-align:center; font-size:15px; font-weight:600; color:#4b5563; margin-bottom:8px;">
Precedents
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280; margin-top:0;">
This section contains information related to precedents issued by the SCJN.
These precedents are guiding judicial criteria with highly relevant legal content.<br><br>

In <strong>“Areas”</strong>, you will find a ranking of subject areas throughout the year.
Rank 1 corresponds to the most common area, while rank 6 corresponds to the area with the fewest precedents issued.<br><br>

In <strong>“Totals by Justice”</strong>, you will find a heatmap showing precedents issued
by each justice over time.<br><br>

In <strong>“By Type”</strong>, you will find the total number of precedents by type
(isolated precedent or jurisprudencia). Unlike isolated precedents, jurisprudencia refers to binding criteria
for lower courts below the SCJN.<br><br>

In <strong>“Main Topics”</strong>, you can explore the most relevant themes found in precedent headings
by judicial era.<br><br>

This analysis includes information from 2015 onward
(except for <strong>“Main Topics”</strong>, which includes all judicial eras since 1920).
</p>

</div>""",
            unsafe_allow_html=True,
        )

    with sub1:
        st.altair_chart(tesis_materias_chart, use_container_width=True)

    with sub2:
        st.altair_chart(tesis_heatmap, use_container_width=True)

    with sub3:
        st.altair_chart(tesis_por_tipo_chart, use_container_width=True)

    with sub4:
        render_ngrams_tesis_tab()

# Declaraciones tab
with tab_declaraciones:
    st.header("Declaraciones (Disclosures)")

    sub0, sub1, sub2, sub3 = st.tabs(
        [
            "Overview",
            "Nivel educativo (Educational level)",
            "Bienes inmuebles (Assets)",
            "Salarios (Salaries)",
        ]
    )

    with sub0:
        st.markdown(
            """<div style="max-width:1050px; margin:0 auto 24px auto; line-height:1.75;">

<p style="text-align:center; font-size:20px; font-weight:600; color:#2f3343; margin-bottom:14px;">
Declaraciones
</p>

<p style="text-align:justify; font-size:15px; color:#374151; margin-bottom:12px;">
En esta parte podrás encontrar información vinculada con las declaraciones patrimoniales y de intereses
de las y los ministros en los últimos dos años (2024 y 2025).<br><br>

En la pestaña <strong>“Nivel educativo”</strong>, podrás encontrar una tabla que contiene
los niveles educativos más altos reportados por las y los ministros.<br><br>

En la pestaña <strong>“Bienes inmuebles”</strong>, podrás encontrar los bienes inmuebles declarados
por los ministros.<br><br>

En la pestaña <strong>“Salarios”</strong>, podrás encontrar los sueldos declarados por las y los ministros.
</p>

<hr style="margin:24px 0; opacity:0.20;">

<p style="text-align:center; font-size:15px; font-weight:600; color:#4b5563; margin-bottom:8px;">
Disclosures
</p>

<p style="text-align:justify; font-size:13px; color:#6b7280; margin-top:0;">
This section contains information related to the financial and conflict-of-interest disclosures
of Supreme Court justices for the last two years (2024 and 2025).<br><br>

In <strong>“Educational Level”</strong>, you will find a table with the highest educational levels
reported by the justices.<br><br>

In <strong>“Assets”</strong>, you will find declared real estate properties.<br><br>

In <strong>“Salaries”</strong>, you will find the salaries reported by the justices.
</p>

</div>""",
            unsafe_allow_html=True,
        )

    with sub1:
        st.subheader(
            "Nivel educativo más alto declarado por persona (Highest educational level declared)"
        )
        edu_table = build_edu_table(declaraciones)
        st.dataframe(edu_table, use_container_width=True, hide_index=True)

    with sub2:
        st.subheader("Bienes inmuebles (Assets)")
        inmuebles_table = build_inmuebles_table(declaraciones_inmuebles)
        st.dataframe(inmuebles_table, use_container_width=True, hide_index=True)

    with sub3:
        st.subheader("Salario declarado (Declared salary)")
        salary_table = build_salary_table(declaraciones)
        st.dataframe(salary_table, use_container_width=True, hide_index=True)
