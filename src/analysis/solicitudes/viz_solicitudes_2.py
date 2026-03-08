"""
This file was to test the solicitudes tab for the streamlit dashboard. 
It does two main things: shows a bar chart of how many times each minister is mentioned 
in solicitudes for a selected year, and it lets the user run an interative 
salient ngrams analysis by minister, year and ngram size.
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


def return_ministers_bar_chart(df, selected_year):
    """Bar chart of counts a minister is mentioned in a request"""
    # keep only one year 
    df_year = df[df["year"] == str(selected_year)].copy()

    # empty chart if there is no data for that year 
    if df_year.empty:
        return alt.Chart(pd.DataFrame({"minister": [], "count": []})).mark_bar()

    # format minister names and sort so most common are first
    df_year["minister"] = df_year["minister"].astype(str).str.title()
    df_year = df_year.sort_values("count", ascending=False)
    #chart, count on x, minister on y
    chart = (
        alt.Chart(df_year)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Menciones"),
            y=alt.Y("minister:N", sort="-x", title="Ministro/a"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=["minister", "count"],
        )
        .properties(height=500)
    )
    return chart


def render_solicitudes_tab(solicitudes_counts):
    st.header("⚖️ Análisis de Solicitudes SCJN")
    
    # subtabs within solicitudes viz
    subtab_mentions, subtab_themes = st.tabs(
        ["📊 Menciones a Ministros", "🔤 Temas Principales (N-grams)"]
    )

    # bar chart 
    with subtab_mentions:
        st.subheader("Which SCJN ministers are mentioned the most by citizens?")
        # build year selector from values that actually exist in the data
        available_years = sorted(
            solicitudes_counts["year"].dropna().unique(), reverse=True
        )
        # use cols so the selector ans summmary metric side by side
        col_filter, col_metric = st.columns([1, 2])

        # dropdown to choose which year to display in the mentions chart 
        with col_filter:
            selected_year = st.selectbox(
                "Select year:",
                available_years,
                key="solicitudes_mentions_year",
            )

        df_year = solicitudes_counts[solicitudes_counts["year"] == str(selected_year)]
        # only show chart if the selected year has counts 
        if not df_year.empty and df_year["count"].sum() > 0:
            chart_ministers = return_ministers_bar_chart(
                solicitudes_counts, selected_year
            )
            top_row = df_year.sort_values("count", ascending=False).iloc[0]
            # highlight most mentioned 
            with col_metric:
                st.metric(
                    label=f"Most mentioned ({selected_year})",
                    value=str(top_row["minister"]).title(),
                    delta=f"{int(top_row['count'])} registros",
                )
            # render altair chart 
            st.altair_chart(chart_ministers, use_container_width=True)
        else:
            st.warning("No data available for this year")

    # Ngrams
    with subtab_themes:
        st.subheader("Salient N-grams (TF-IDF) by minister")
        # main controls 
        col1, col2, col3 = st.columns(3)
        # use ministers in data as the selectbox options
        available_ministers = sorted(
            solicitudes_counts["minister"].dropna().astype(str).unique()
        )
        with col1:
            selected_year_themes = st.selectbox(
                "Year:", available_years, key="themes_year"
            )
        with col2:
            selected_minister = st.selectbox(
                "Minister:", available_ministers, key="themes_minister"
            )
        with col3:
            n_size = st.selectbox("Size (n-gram):", [1, 2, 3], index=1)

        top_k = st.slider("Number of themes to show:", 3, 15, 8)

        # call the ngram analysis when the parameters are selected by user
        if st.button("Execute theme analysis"):
            try:
                data_list = analyze_themes(
                    csv_path=SOLICITUDES_TEXT_CSV,
                    n_size=n_size,
                    top_k=top_k,
                    filter_name=selected_minister,
                )
                if data_list:
                     # convert result list into a df so its easy to filter  
                    themes_df = pd.DataFrame(data_list)
                    # filter result by year
                    themes_year = themes_df[
                        themes_df["year"] == str(selected_year_themes)
                    ]

                    if themes_year.empty:
                        st.info("None for this minister")
                    else:
                        display_df = themes_year[["ngram", "count", "score"]].rename(
                            columns={
                                "ngram": "N-gram",
                                "count": "Frequency",
                                "score": "Relevancy (Score)",
                            }
                        )
                        st.dataframe(
                            display_df, hide_index=True, use_container_width=True
                        )
                else:
                    st.warning("No requests for this filter")

            except FileNotFoundError:
                st.error(f"Error: missing file {SOLICITUDES_TEXT_CSV}")


if __name__ == "__main__":
    # load counts for app
    if SOLICITUDES_COUNTS_CSV.exists():
        df_counts = pd.read_csv(SOLICITUDES_COUNTS_CSV)
        df_counts["year"] = df_counts["year"].astype(str)
        render_solicitudes_tab(df_counts)
    else:
        st.error(f"Missing count ministros file: {SOLICITUDES_COUNTS_CSV}")
