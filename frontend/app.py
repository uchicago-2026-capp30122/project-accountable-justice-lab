import streamlit as st
import pandas as pd
import altair as alt
import csv
import math
import unicodedata
from pathlib import Path
from collections import Counter
from viz_solicitudes import return_ministers_bar_chart

# Page configuration
st.set_page_config(page_title="Accountable Justice Lab", layout="wide")

st.title("⚖️ OJO PIOJO")
st.write("Accountable Justice Lab")
st.image("frontend/ojopiojo.jpeg", width=100)

# File paths
SOLICITUDES_COUNTS_CSV = "todos_los_ministros_timeseries.csv"
SOLICITUDES_TEXT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"
TESIS_CSV = "frontend/tesis_joined_data.csv"
SENTENCIAS_CSV = "frontend/sentencias_joined_data.csv"
DECLARACIONES_XLSX = "frontend/declaraciones/final_variables.xlsx"


# Stopwords for salient token analysis
STOPWORDS = {
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    "y",
    "o",
    "u",
    "e",
    "de",
    "del",
    "al",
    "a",
    "en",
    "por",
    "para",
    "con",
    "sin",
    "sobre",
    "que",
    "como",
    "cuando",
    "donde",
    "cada",
    "uno",
    "este",
    "esta",
    "quien",
    "se",
    "su",
    "sus",
    "mi",
    "mis",
    "me",
    "te",
    "le",
    "les",
    "lo",
    "nos",
    "no",
    "sí",
    "si",
    "ya",
    "más",
    "menos",
    "muy",
    "tan",
    "también",
    "tampoco",
    "todo",
    "toda",
    "todos",
    "todas",
    "mismo",
    "misma",
    "así",
    "asi",
    "vez",
    "día",
    "dia",
    "año",
    "ano",
    "parte",
    "partes",
    "estos",
    "estas",
    "esos",
    "esas",
    "aquello",
    "aquella",
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
    "mes",
    "meses",
    "periodo",
    "lapso",
    "comprendido",
    "durante",
    "actual",
    "pasado",
    "presente",
    "fecha",
    "fechas",
    "http",
    "https",
    "www",
    "com",
    "mx",
    "html",
    "php",
    "aspx",
    "url",
    "sitio",
    "web",
    "enlace",
    "link",
    "archivo",
    "pdf",
    "formatos",
    "imagen",
    "jpg",
    "png",
    "clic",
    "click",
    "adjunto",
    "adjunta",
    "anexo",
    "anexa",
    "descargar",
    "solicitud",
    "solicito",
    "solicita",
    "solicitante",
    "información",
    "informacion",
    "pública",
    "publica",
    "favor",
    "pudieran",
    "ser",
    "ha",
    "he",
    "fue",
    "son",
    "es",
    "unir",
    "hacer",
    "solicitar",
    "atentamente",
    "cordial",
    "saludo",
    "gracias",
    "trasparencia",
    "unidad",
    "acceso",
    "folio",
    "respuesta",
    "oficio",
    "escrito",
    "presentado",
    "mediante",
    "través",
    "traves",
    "medio",
    "proporcione",
    "entregue",
    "haga",
    "llegar",
    "pueda",
    "dar",
    "conocer",
    "copia",
    "copias",
    "versión",
    "version",
    "documento",
    "documentos",
    "expediente",
    "número",
    "numero",
    "registrado",
    "ingresado",
    "scjn",
    "suprema",
    "corte",
    "justicia",
    "nación",
    "nacion",
    "poder",
    "judicial",
    "federal",
    "ley",
    "artículo",
    "articulo",
    "art",
    "fracción",
    "fraccion",
    "inciso",
    "párrafo",
    "parrafo",
    "tesis",
    "jurisprudencia",
    "rubro",
    "sentencia",
    "ejecutoria",
    "amparo",
    "directo",
    "indirecto",
    "revisión",
    "revision",
    "sala",
    "tribunal",
    "colegiado",
    "circuito",
    "asunto",
    "asuntos",
    "acuerdo",
    "resolución",
    "resolucion",
    "votos",
    "voto",
    "ponente",
    "ministro",
    "ministra",
    "secretario",
    "actuaria",
    "[…]",
    "[...]",
    "...",
    "….",
    "señala",
    "señalada",
    "senala",
    "senalada",
    "punto",
    "puntos",
    "literal",
    "referencia",
    "relación",
    "relacion",
    "respecto",
    "dicho",
    "dicha",
    "mencionada",
    "citada",
    "tal",
    "tales",
    "sujeto",
    "obligado",
    "tiene",
    "tienen",
    "don",
    "lic",
    "está",
    "esta",
    "mexicanos",
    "mexicano",
    "mexicana",
    "peso",
    "pesos",
    "dinero",
    "adquirido",
    "adquiridos",
    "adquisicion",
    "cual",
    "cuales",
    "quiere",
    "quisiera",
    "tipo",
    "materia",
    "versaron",
    "pertenecientes",
    "dictada",
    "respectiva",
    "fueron",
    "presenta",
    "ejercicio",
    "posible",
    "incluyendo",
    "hayan",
    "sea",
    "manera",
    "tambien",
    "debidamente",
    "caracter",
    "respetuosamente",
    "disponible",
    "mensualmente",
    "anual",
    "mas",
    "total",
    "millones",
    "mil",
    "tomo",
    "pagina",
    "paginas",
    "modulo",
    "tramitada",
    "derivo",
    "tratar",
    "danar",
    "otro",
    "otra",
    "otros",
    "otras",
    "aquellos",
    "aquellas",
    "general",
    "nacional",
    "social",
    "universidad",
    "directora",
    "director",
    "escuela",
    "comunicado",
    "firmado",
    "emision",
    "digital",
    "electronica",
    "fisica",
    "empresa",
    "nombre",
    "persona",
    "personas",
    "sentido",
    "amplio",
    "entradas",
    "salidas",
    "bienes",
    "entregado",
    "elementos",
    "causas",
    "procesos",
    "presuntos",
    "responsables",
    "irregularidades",
    "administrativas",
    "ordenadoras",
    "validez",
    "mayor",
    "autorizada",
    "juridica",
    "unifamiliar",
    "identificacion",
    "comparte",
    "proyectado",
    "corresponda",
    "contradicción",
    "criterio",
    "criterios",
    "usted",
    "enviar",
    "ponencia",
    "tu",
    "tus",
    "realizado",
    "estados",
    "unidos",
    "código",
    "codigo",
    "reglamento",
    "constitucion",
    "constitución",
    "buenas",
    "tardes",
    "han",
    "sido",
    "¿cual",
    "motivo",
    "semanario",
    "dirección",
    "institución",
    "legal",
    "hasta",
    "¿cuál",
    "denominado",
}


# Cached data loaders
@st.cache_data
def load_main_data():
    """Load all dashboard datasets only once."""
    tesis = pd.read_csv(TESIS_CSV, dtype=str, index_col=0)
    sentencias = pd.read_csv(SENTENCIAS_CSV, dtype=str, index_col=0)
    declaraciones = pd.read_excel(DECLARACIONES_XLSX)
    solicitudes_counts = pd.read_csv(SOLICITUDES_COUNTS_CSV)

    solicitudes_counts["year"] = solicitudes_counts["year"].astype(str)

    return tesis, sentencias, declaraciones, solicitudes_counts


@st.cache_data
def load_solicitudes_text():
    """Load the cleaned solicitudes text file used for salient token analysis."""
    return pd.read_csv(SOLICITUDES_TEXT_CSV, dtype=str)


tesis, sentencias, declaraciones, solicitudes_counts = load_main_data()


# Text processing helpers
def normalize_text(text):
    """
    Normalize text by:
    - lowercasing
    - removing accents
    - removing selected punctuation
    - collapsing multiple spaces
    """
    if pd.isna(text) or not text:
        return ""

    text = str(text).lower()

    # Remove accents
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )

    # Replace punctuation with spaces
    for char in ".,?!():;\"'¿¡":
        text = text.replace(char, " ")

    return " ".join(text.split())


def jaro_winkler(s1, s2):
    """
    Compute Jaro-Winkler similarity between two strings.
    Returns a value between 0.0 and 1.0.
    """
    s1, s2 = s1.lower(), s2.lower()

    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    max_dist = max(len1, len2) // 2 - 1

    match = 0
    hash_s1 = [0] * len1
    hash_s2 = [0] * len2

    # Find matching characters
    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    if match == 0:
        return 0.0

    # Count transpositions
    t = 0
    point = 0
    for i in range(len1):
        if hash_s1[i]:
            while hash_s2[point] == 0:
                point += 1
            if s1[i] != s2[point]:
                t += 1
            point += 1

    t //= 2

    # Jaro score
    jaro = (1 / 3) * (match / len1 + match / len2 + (match - t) / match)

    # Winkler prefix bonus
    p = 0.1
    l = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            l += 1
        else:
            break

    return jaro + (l * p * (1 - jaro))


def is_mentioning(text, target_name, threshold=0.92):
    """
    Check whether a target name appears in text using:
    1. exact substring match after normalization
    2. fuzzy matching on individual name parts
    """
    normalized_target = normalize_text(target_name)

    if normalized_target in text:
        return True

    target_parts = normalized_target.split()
    words = text.split()

    for part in target_parts:
        if len(part) < 4:
            continue
        for word in words:
            if jaro_winkler(word, part) >= threshold:
                return True

    return False


def get_ngrams(text, n):
    """
    Build n-grams after removing stopwords and very short words.
    """
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


# Dashboard helper functions
def return_materias_chart(tesis_df):
    """
    Build the tesis chart showing the ranking of main topics by year.
    """
    materias = (
        tesis_df.groupby(["anio", "main_materia"])["idTesis"]
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


def build_edu_table(declaraciones_df):
    """
    Build the declarations table showing highest education level per person.
    """
    edu_por_persona = (
        declaraciones_df.groupby(["nombre", "primer_apellido", "segundo_apellido"])[
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

    return edu_por_persona


@st.cache_data
def analyze_themes(csv_path, n_size=2, top_k=8, filter_name=None):
    """
    Analyze salient themes by year using a TF-IDF-like approach.

    Parameters:
    - csv_path: path to the cleaned solicitudes CSV
    - n_size: size of the n-gram
    - top_k: number of top themes per year
    - filter_name: minister to filter by

    Returns:
    - DataFrame with columns: year, ngram, count, score, minister
    """
    year_docs = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            year = row.get("year")
            if not year or not year.isdigit() or int(year) < 2017:
                continue

            raw_text = row.get("DescripcionSolicitud", "")
            clean_text = normalize_text(raw_text)

            if len(clean_text) < 10:
                continue

            # If a minister filter is provided, keep only rows mentioning that minister
            if filter_name:
                if not is_mentioning(clean_text, filter_name):
                    continue

            ngrams = get_ngrams(clean_text, n_size)
            if not ngrams:
                continue

            if year not in year_docs:
                year_docs[year] = []

            year_docs[year].extend(ngrams)

    if not year_docs:
        return pd.DataFrame(columns=["year", "ngram", "count", "score", "minister"])

    all_years = list(year_docs.keys())
    num_years = len(all_years)

    # Count in how many years each n-gram appears
    ngram_year_counts = {}
    for year, ngrams in year_docs.items():
        for gram in set(ngrams):
            ngram_year_counts[gram] = ngram_year_counts.get(gram, 0) + 1

    rows = []

    for year in sorted(all_years, key=int):
        ngrams_in_year = year_docs[year]
        counts = Counter(ngrams_in_year)
        total = len(ngrams_in_year)

        scores = []
        for gram, count in counts.items():
            tf = count / total
            idf = (
                math.log(num_years / ngram_year_counts[gram]) if num_years > 1 else 1.0
            )
            scores.append((gram, tf * idf, count))

        top_themes = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

        for gram, score, count in top_themes:
            rows.append(
                {
                    "year": str(year),
                    "ngram": gram,
                    "count": count,
                    "score": score,
                    "minister": filter_name if filter_name else "All",
                }
            )

    return pd.DataFrame(rows)


# Main tabs
tab_general, tab_solicitudes, tab_sentencias, tab_tesis, tab_declaraciones = st.tabs(
    ["General", "Solicitudes", "Sentencias", "Tesis", "Declaraciones"]
)

# General tab
with tab_general:
    st.header("General")

    chart_general = return_materias_chart(tesis)
    st.altair_chart(chart_general, use_container_width=True)

# Solicitudes tab
with tab_solicitudes:
    st.header("Solicitudes")

    # Create internal tabs only for the Solicitudes section
    subtab_mentions, subtab_themes = st.tabs(
        ["📊 Menciones a Ministros", "🔤 Temas Principales (N-grams)"]
    )

    # Subtab: Minister mentions
    with subtab_mentions:
        st.subheader("¿A qué ministros mencionan más los ciudadanos?")

        col_filter, col_metric = st.columns([1, 2])

        with col_filter:
            available_years = sorted(
                solicitudes_counts["year"].dropna().unique(), reverse=True
            )
            selected_year = st.selectbox(
                "Selecciona el año a visualizar:",
                available_years,
                key="solicitudes_mentions_year",
            )

        df_year = solicitudes_counts[solicitudes_counts["year"] == str(selected_year)]

        if not df_year.empty and df_year["count"].sum() > 0:
            chart_ministers = return_ministers_bar_chart(
                solicitudes_counts, selected_year
            )
            top_row = df_year.sort_values("count", ascending=False).iloc[0]

            with col_metric:
                st.metric(
                    label=f"Ministro más mencionado en {selected_year}",
                    value=str(top_row["minister"]).title(),
                    delta=f"{int(top_row['count'])} menciones",
                )

            st.altair_chart(chart_ministers, use_container_width=True)
        else:
            st.warning("No hay datos de ministros para este año.")

    # Subtab: Salient themes
    with subtab_themes:
        st.subheader("Temas principales por ministro")

        col1, col2, col3 = st.columns(3)

        available_years_themes = sorted(
            solicitudes_counts["year"].dropna().unique(), reverse=True
        )

        available_ministers = sorted(
            solicitudes_counts["minister"].dropna().astype(str).unique()
        )

        with col1:
            selected_year_themes = st.selectbox(
                "Year", available_years_themes, key="themes_year"
            )

        with col2:
            selected_minister = st.selectbox(
                "Minister", available_ministers, key="themes_minister"
            )

        with col3:
            n_size = st.selectbox(
                "N-gram size", [1, 2, 3], index=1, key="themes_ngram_size"
            )

        top_k = st.slider(
            "Number of top themes", min_value=3, max_value=15, value=8, step=1
        )

        try:
            themes_df = analyze_themes(
                csv_path=SOLICITUDES_TEXT_CSV,
                n_size=n_size,
                top_k=top_k,
                filter_name=selected_minister,
            )

            themes_year = themes_df[
                themes_df["year"] == str(selected_year_themes)
            ].copy()

            if themes_year.empty:
                st.warning(
                    "No hay temas disponibles para esa combinación de año y ministro."
                )
            else:
                themes_year = themes_year.sort_values(
                    by=["score", "count"], ascending=False
                )

                display_df = themes_year[["ngram", "count", "score"]].rename(
                    columns={
                        "ngram": "Tema",
                        "count": "Menciones",
                        "score": "TF-IDF score",
                    }
                )

                st.dataframe(display_df, hide_index=True, use_container_width=True)

        except FileNotFoundError:
            st.error(
                "The file clean_output/clean_solicitudes_2017_2026.csv was not found."
            )

# Sentencias tab
with tab_sentencias:
    st.header("Sentencias")
    st.write("Here you can add the visualizations for sentencias.")

# Tesis tab
with tab_tesis:
    st.header("Tesis")
    st.write("Here you can add the visualizations for tesis.")

# Declaraciones tab
with tab_declaraciones:
    st.header("Declaraciones")
    st.subheader("Nivel educativo por persona")

    edu_por_persona = build_edu_table(declaraciones)
    st.dataframe(edu_por_persona, use_container_width=True)
