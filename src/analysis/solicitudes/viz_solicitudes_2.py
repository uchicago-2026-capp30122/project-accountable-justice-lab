"""
This file was to test the solicitudes tab for the streamlit dashboard. 
It does 3 main things: shows a bar chart of how many times each minister is mentioned 
in solicitudes for a selected year, and it lets the user run an interative 
salient ngrams analysis by minister, year and ngram size, 
and finally shows in a third tab the no response index graph and chart. 
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[3]
sys.path.append(str(root_path))

from src.analysis.solicitudes.salient_tokens_solicitudes import analyze_themes

SOLICITUDES_COUNTS_CSV = Path("data/viz_data/todos_los_ministros_timeseries.csv")
SOLICITUDES_TEXT_CSV = Path(
"data/clean_data/solicitudes/clean_solicitudes_2017_2026.csv"
)
SOLICITUDES_INDEX_CSV = Path("data/viz_data/noresponse_index_solicitudes.csv")

def return_ministers_bar_chart(df, selected_year):
    """Bar chart of counts a minister is mentioned in a request"""
    # keep only one year 
    df_year = df[df["year"] == str(selected_year)].copy()

    # empty chart if there is no data for that year 
    if df_year.empty:
        return alt.Chart(pd.DataFrame({"minister": [], "count": []})).mark_bar()

    # format minister names and sort so most common are first
    df_year["minister"] = df_year["minister"].astype(str).str.title()
    df_year = df_year.sort_values("count", ascending=False).reset_index(drop=True)
    df_year['highlight'] = df_year.index == 0
    #chart, count on x, minister on y
    chart = (
        alt.Chart(df_year)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Menciones (Counts)"),
            y=alt.Y("minister:N", sort="-x", title="Ministro (Justice)"),
            color=alt.condition(
                alt.datum.highlight,
                alt.value("#1269a7"),  
                alt.value("#3769A6")  
            ),
            tooltip=["minister", "count"],
        )
        .properties(height=500)
    )
    return chart

def return_no_response_line_chart(df):
    """time series chart of non-response index by year"""
    chart_df = df.copy()
    chart_df["year"] = pd.to_numeric(chart_df["year"], errors="coerce")
    chart_df["no_response_percent"] = chart_df["no_response_index"] * 100
    chart_df = chart_df.dropna(subset=["year", "no_response_percent"]).sort_values("year")

    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Año (Year)"),
            y=alt.Y("no_response_percent:Q", title="No respuesta (no response) (%)"),
            tooltip=[
                alt.Tooltip("year:O", title="Año"),
                alt.Tooltip("no_response_percent:Q", title="No respuesta (no response) (%)", format=".2f"),
            ],
        )
        .properties(height=250)
    )

    return chart


def render_solicitudes_tab(solicitudes_counts, solicitudes_index):
    st.header("Solicitudes (Requests)")
    available_years = sorted(
        solicitudes_counts["year"].dropna().unique(), reverse=True
    )

    # use ministers in data as the selectbox options
    available_ministers = sorted(
        solicitudes_counts["minister"].dropna().astype(str).unique()
    )

    # subtabs within solicitudes viz
    subtab_overview, subtab_mentions, subtab_themes, subtab_index = st.tabs(
        [
            "Overview",
            "Menciones a Ministros (Minister Count)",
            "Temas Principales (N-grams)",
            "Índice de No Respuesta (No Response Rate)",
        ]
    )

    with subtab_overview:
        st.markdown(
    """
    <div style="max-width:1050px; margin:0 auto 24px auto; line-height:1.75;">

    <p style="text-align:center; font-size:20px; font-weight:600; color:#2f3343; margin-bottom:14px;">
        Solicitudes
    </p>

    <p style="text-align:justify; font-size:15px; color:#374151; margin-bottom:12px;">
        En esta pestaña podrás encontrar análisis referente a las solicitudes de información realizadas por la ciudadanía
        a través de la Plataforma Nacional de Transparencia, con especial énfasis a menciones y temáticas relacionadas
        con las y los ministros de la SCJN.
        <br><br>
        En la pestaña <strong>“Menciones a Ministros”</strong>, encontrarás una gráfica de barras que muestra el conteo
        de las veces que fueron mencionadas y mencionados las y los ministros en las solicitudes de información.
        <br><br>
        En la pestaña <strong>“Temas Principales”</strong>, podrás seleccionar los temas más relevantes por año
        y por ministra/ministro.
        <br><br>
        En la pestaña <strong>“Índice de No Respuesta”</strong>, se encuentra un índice agregado de la tasa de no respuesta
        por parte de la SCJN a solicitudes de información (no respuesta se entiende como que no hubo entrega de información
        por parte de la institución a la persona ciudadana).
        <br><br>
        El análisis incluye información de 2017 a la fecha.
    </p>

    <hr style="margin:24px 0; opacity:0.20;">

    <p style="text-align:center; font-size:15px; font-weight:600; color:#4b5563; margin-bottom:8px;">
        Requests
    </p>

    <p style="text-align:justify; font-size:13px; color:#6b7280; margin-top:0;">
        This section presents analysis of public information requests submitted by citizens through Mexico’s National
        Transparency Platform, with special emphasis on mentions of Supreme Court justices and the main themes related
        to them.
        <br><br>
        In <strong>“Mentions to Justices”</strong>, you will find a bar chart showing how many times each justice
        was mentioned in information requests.
        <br><br>
        In <strong>“Main Topics”</strong>, you can explore the most relevant themes by year and by justice.
        <br><br>
        In <strong>“Non-response Index”</strong>, you will find an aggregate index of the SCJN’s non-response rate
        to information requests. Non-response means that the institution did not provide information to the citizen requester.
        <br><br>
        This analysis includes information from 2017 onward.
    </p>

    </div>
    """,
            unsafe_allow_html=True,
        )

    # Mentions
    with subtab_mentions:
        st.subheader("¿A qué ministros mencionan más los ciudadanos?")
        st.caption("Which ministers are mentioned the most by citizens?")

        # use cols so the selector and summary metric sit side by side
        col_filter, col_metric = st.columns([1, 2])

        with col_filter:
            selected_year = st.selectbox(
                "Seleccionar año (Year):",
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
                    label=f"Líder en menciones (Most mentioned) ({selected_year})",
                    value=str(top_row["minister"]).title(),
                    delta=f"{int(top_row['count'])} registros",
                )

            st.altair_chart(chart_ministers, use_container_width=True)
        else:
            st.warning("No data available for this year.")

    # Themes
    with subtab_themes:
        st.subheader("Temas salientes (TF-IDF) por ministro por año")
        st.caption("Salient tokens by justice by year")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_year_themes = st.selectbox(
                "Año (Year):", available_years, key="themes_year"
            )
        with col2:
            selected_minister = st.selectbox(
                "Ministro (Justice):", available_ministers, key="themes_minister"
            )
        with col3:
            n_size = st.selectbox("Tamaño (n-gram):", [1, 2, 3], index=1)

        top_k = st.slider("Número de n-grams:", 3, 15, 8)

        if st.button("Ejecutar análisis (Execute n-gram analysis)"):
            try:
                data_list = analyze_themes(
                    csv_path=SOLICITUDES_TEXT_CSV,
                    n_size=n_size,
                    top_k=top_k,
                    filter_name=selected_minister,
                )

                if data_list:
                    themes_df = pd.DataFrame(data_list)
                    themes_year = themes_df[
                        themes_df["year"] == str(selected_year_themes)
                    ]

                    if themes_year.empty:
                        st.info("No themes available for this justice in the selected year.")
                    else:
                        display_df = themes_year[["ngram", "count", "score"]].rename(
                            columns={
                                "ngram": "N-gram",
                                "count": "Frecuencia (Frequency)",
                                "score": "Relevancia (Score)",
                            }
                        )
                        st.dataframe(
                            display_df,
                            hide_index=True,
                            use_container_width=True,
                        )
                else:
                    st.warning("No requests available for this filter")

            except FileNotFoundError:
                st.error(f"Error: missing file {SOLICITUDES_TEXT_CSV}")

    # No response index
    with subtab_index:
        st.subheader("Índice de no respuesta por año")
        st.caption("No response rate per year")

        if solicitudes_index.empty:
            st.info("No hay datos disponibles. No available data.")
        else:
            display_index = solicitudes_index.copy()
            display_index["year"] = display_index["year"].astype(str)
            display_index["no_response_percent"] = (
                display_index["no_response_index"] * 100
            ).round(2)

            row_2025 = display_index[display_index["year"] == "2025"]

            if not row_2025.empty:
                metric_row = row_2025.iloc[0]
            else:
                metric_row = display_index.sort_values("year", ascending=False).iloc[0]

            col_metric, col_chart = st.columns([1, 2])

            with col_metric:
                st.metric(
                    label=f"No respuesta en {metric_row['year']}",
                    value=f"{metric_row['no_response_percent']:.2f}%",
                )

            with col_chart:
                chart_no_response = return_no_response_line_chart(display_index)
                st.altair_chart(chart_no_response, use_container_width=True)

            table_df = display_index[["year", "no_response_percent"]].rename(
                columns={
                    "year": "Año",
                    "no_response_percent": "Índice de No Respuesta (%)",
                }
            )

            st.dataframe(table_df, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    if SOLICITUDES_COUNTS_CSV.exists() and SOLICITUDES_INDEX_CSV.exists():
        df_counts = pd.read_csv(SOLICITUDES_COUNTS_CSV)
        df_counts["year"] = df_counts["year"].astype(str)
        df_index = pd.read_csv(SOLICITUDES_INDEX_CSV)
        df_index['year'] = df_index['year'].astype(str)
        render_solicitudes_tab(df_counts, df_index)
    else:
        st.error(f"Missing file for counts or index")
