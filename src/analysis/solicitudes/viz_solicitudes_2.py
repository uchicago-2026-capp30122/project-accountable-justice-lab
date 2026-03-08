import streamlit as st
import pandas as pd
import altair as alt
import csv
import math
import unicodedata
from pathlib import Path
from collections import Counter

SOLICITUDES_TEXT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"

# Stopwords for salient token analysis
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "u", "e",
    "de", "del", "al", "a", "en", "por", "para", "con", "sin", "sobre", "que",
    "como", "cuando", "donde", "cada", "uno", "este", "esta", "quien", "se",
    "su", "sus", "mi", "mis", "me", "te", "le", "les", "lo", "nos", "no", "sí",
    "si", "ya", "más", "menos", "muy", "tan", "también", "tampoco", "todo",
    "toda", "todos", "todas", "mismo", "misma", "así", "asi", "vez", "día",
    "dia", "año", "ano", "parte", "partes", "estos", "estas", "esos", "esas",
    "aquello", "aquella", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "mes",
    "meses", "periodo", "lapso", "comprendido", "durante", "actual", "pasado",
    "presente", "fecha", "fechas", "http", "https", "www", "com", "mx", "html",
    "php", "aspx", "url", "sitio", "web", "enlace", "link", "archivo", "pdf",
    "formatos", "imagen", "jpg", "png", "clic", "click", "adjunto", "adjunta",
    "anexo", "anexa", "descargar", "solicitud", "solicito", "solicita",
    "solicitante", "información", "informacion", "pública", "publica", "favor",
    "pudieran", "ser", "ha", "he", "fue", "son", "es", "unir", "hacer",
    "solicitar", "atentamente", "cordial", "saludo", "gracias", "trasparencia",
    "unidad", "acceso", "folio", "respuesta", "oficio", "escrito", "presentado",
    "mediante", "través", "traves", "medio", "proporcione", "entregue", "haga",
    "llegar", "pueda", "dar", "conocer", "copia", "copias", "versión", "version",
    "documento", "documentos", "expediente", "número", "numero", "registrado",
    "ingresado", "scjn", "suprema", "corte", "justicia", "nación", "nacion",
    "poder", "judicial", "federal", "ley", "artículo", "articulo", "art",
    "fracción", "fraccion", "inciso", "párrafo", "parrafo", "tesis",
    "jurisprudencia", "rubro", "sentencia", "ejecutoria", "amparo", "directo",
    "indirecto", "revisión", "revision", "sala", "tribunal", "colegiado",
    "circuito", "asunto", "asuntos", "acuerdo", "resolución", "resolucion",
    "votos", "voto", "ponente", "ministro", "ministra", "secretario", "actuaria",
    "[…]", "[...]", "...", "….", "señala", "señalada", "senala", "senalada",
    "punto", "puntos", "literal", "referencia", "relación", "relacion",
    "respecto", "dicho", "dicha", "mencionada", "citada", "tal", "tales",
    "sujeto", "obligado", "tiene", "tienen", "don", "lic", "está", "esta",
    "mexicanos", "mexicano", "mexicana", "peso", "pesos", "dinero", "adquirido",
    "adquiridos", "adquisicion", "cual", "cuales", "quiere", "quisiera", "tipo",
    "materia", "versaron", "pertenecientes", "dictada", "respectiva", "fueron",
    "presenta", "ejercicio", "posible", "incluyendo", "hayan", "sea", "manera",
    "tambien", "debidamente", "caracter", "respetuosamente", "disponible",
    "mensualmente", "anual", "mas", "total", "millones", "mil", "tomo", "pagina",
    "paginas", "modulo", "tramitada", "derivo", "tratar", "danar", "otro", "otra",
    "otros", "otras", "aquellos", "aquellas", "general", "nacional", "social",
    "universidad", "directora", "director", "escuela", "comunicado", "firmado",
    "emision", "digital", "electronica", "fisica", "empresa", "nombre", "persona",
    "personas", "sentido", "amplio", "entradas", "salidas", "bienes", "entregado",
    "elementos", "causas", "procesos", "presuntos", "responsables",
    "irregularidades", "administrativas", "ordenadoras", "validez", "mayor",
    "autorizada", "juridica", "unifamiliar", "identificacion", "comparte",
    "proyectado", "corresponda", "contradicción", "criterio", "criterios",
    "usted", "enviar", "ponencia", "tu", "tus", "realizado", "estados", "unidos",
    "código", "codigo", "reglamento", "constitucion", "constitución", "buenas",
    "tardes", "han", "sido", "¿cual", "motivo", "semanario", "dirección",
    "institución", "legal", "hasta", "¿cuál", "denominado",
}


def normalize_text(text):
    if pd.isna(text) or not text:
        return ""

    text = str(text).lower()

    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )

    for char in ".,?!():;\"'¿¡":
        text = text.replace(char, " ")

    return " ".join(text.split())


def jaro_winkler(s1, s2):
    s1, s2 = s1.lower(), s2.lower()

    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    max_dist = max(len1, len2) // 2 - 1

    match = 0
    hash_s1 = [0] * len1
    hash_s2 = [0] * len2

    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    if match == 0:
        return 0.0

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

    jaro = (1 / 3) * (match / len1 + match / len2 + (match - t) / match)

    p = 0.1
    l = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            l += 1
        else:
            break

    return jaro + (l * p * (1 - jaro))


def is_mentioning(text, target_name, threshold=0.92):
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
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


@st.cache_data
def analyze_themes(csv_path, n_size=2, top_k=8, filter_name=None):
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


def return_ministers_bar_chart(df, selected_year):
    df_year = df[df["year"] == str(selected_year)].copy()

    if df_year.empty:
        return alt.Chart(pd.DataFrame({"minister": [], "count": []})).mark_bar()

    df_year["minister"] = df_year["minister"].astype(str).str.title()
    df_year = df_year.sort_values("count", ascending=False)

    chart = (
        alt.Chart(df_year)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Mentions"),
            y=alt.Y("minister:N", sort="-x", title="Minister"),
            tooltip=["minister:N", "count:Q"],
        )
        .properties(height=500)
    )

    return chart


def render_solicitudes_tab(solicitudes_counts):
    st.header("Solicitudes")

    subtab_mentions, subtab_themes = st.tabs(
        ["📊 Menciones a Ministros", "🔤 Temas Principales (N-grams)"]
    )

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
            