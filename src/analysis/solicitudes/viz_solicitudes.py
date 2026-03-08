import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[3]
sys.path.append(str(root_path))

SOLICITUDES_COUNTS_CSV = Path("data/viz_data/todos_los_ministros_timeseries.csv")
SOLICITUDES_NGRAMS_CSV = Path("data/viz_data/ngrams_por_ministro.csv")


def return_ministers_bar_chart(df, selected_year):
    """Bar chart of counts a minister is mentioned in a request"""
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
            color=alt.Color("count:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=["minister", "count"],
        )
        .properties(height=500)
    )
    return chart


def render_solicitudes_tab(solicitudes_counts, solicitudes_ngrams):
    st.header("Análisis de Solicitudes SCJN")

    subtab_mentions, subtab_themes = st.tabs(
        ["📊 Menciones a Ministros", "🔤 Temas Principales (N-grams)"]
    )
    # Bar chart of mentions
    with subtab_mentions:
        st.subheader("¿A qué ministros mencionan más los ciudadanos?")

        available_years = sorted(
            solicitudes_counts["year"].dropna().astype(str).unique(),
            reverse=True,
        )

        col_filter, col_metric = st.columns([1, 2])

        with col_filter:
            selected_year = st.selectbox(
                "Selecciona el año:",
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
                    label=f"Líder en menciones ({selected_year})",
                    value=str(top_row["minister"]).title(),
                    delta=f"{int(top_row['count'])} registros",
                )

            st.altair_chart(chart_ministers, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para este año.")


    # Ngrams 
    with subtab_themes:
        st.subheader("Temas salientes (TF-IDF) por ministro")

        available_years_themes = sorted(
            solicitudes_ngrams["year"].dropna().astype(str).unique(),
            reverse=True,
        )

        available_ministers = sorted(
            solicitudes_ngrams["minister"].dropna().astype(str).unique()
        )

        col1, col2 = st.columns(2)

        with col1:
            selected_year_themes = st.selectbox(
                "Año:",
                available_years_themes,
                key="themes_year",
            )

        with col2:
            selected_minister = st.selectbox(
                "Ministro:",
                available_ministers,
                key="themes_minister",
            )

        themes_year = solicitudes_ngrams[
            (solicitudes_ngrams["year"] == str(selected_year_themes))
            & (solicitudes_ngrams["minister"] == selected_minister)
        ].copy()

        if themes_year.empty:
            st.info("No hay temas disponibles para ese ministro en ese año.")
        else:
            themes_year = themes_year.sort_values("score", ascending=False)

            display_df = themes_year[["ngram", "count", "score"]].rename(
                columns={
                    "ngram": "Tema (N-gram)",
                    "count": "Frecuencia",
                    "score": "Relevancia (Score)",
                }
            )

            st.dataframe(display_df, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    if not SOLICITUDES_COUNTS_CSV.exists():
        st.error(f"Missing count ministros file: {SOLICITUDES_COUNTS_CSV}")

    elif not SOLICITUDES_NGRAMS_CSV.exists():
        st.error(f"Missing ngrams file: {SOLICITUDES_NGRAMS_CSV}")

    else:
        df_counts = pd.read_csv(SOLICITUDES_COUNTS_CSV)
        df_counts["year"] = df_counts["year"].astype(str)

        df_ngrams = pd.read_csv(SOLICITUDES_NGRAMS_CSV)
        df_ngrams["year"] = df_ngrams["year"].astype(str)
        df_ngrams["minister"] = df_ngrams["minister"].astype(str)

        render_solicitudes_tab(df_counts, df_ngrams)