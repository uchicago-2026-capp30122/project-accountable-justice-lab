import streamlit as st
import pandas as pd
from viz_solicitudes import return_ministers_bar_chart

st.set_page_config(page_title="Monitor de la Corte", layout="wide")

st.title("⚖️ OJO PIOJO con la Corte")
st.header("¿A qué ministros mencionan más los ciudadanos?")

@st.cache_data
def get_data():
    # cargar csv
    return pd.read_csv("todos_los_ministros_timeseries.csv")

try:
    df_counts = get_data()
    df_counts['year'] = df_counts['year'].astype(str)

    # sidebar para la seleccion del año
    with st.sidebar:
        st.subheader("Configuración")
        # solo los anos del csv
        available_years = sorted(df_counts['year'].unique(), reverse=True)
        selected_year = st.selectbox("Selecciona el año a visualizar:", available_years)

    df_year = df_counts[df_counts['year'] == str(selected_year)]

    if not df_year.empty and df_year['count'].sum() > 0:
        chart = return_ministers_bar_chart(df_counts, selected_year)

        # metrica del ministro más mencionado (ordenamos de mayor a menor)
        top_row = df_year.sort_values('count', ascending=False).iloc[0]
        
        st.metric(
            label=f"Ministro más mencionado en {selected_year}", 
            value=str(top_row['minister']).title(), 
            delta=f"{int(top_row['count'])} menciones"
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        # si el año existe pero todas las cuentas son 0, o no hay filas:
        st.warning(f"No se encontraron menciones para el año {selected_year} en el archivo de datos")

except FileNotFoundError:
    st.error("No se encontró el archivo, falta correr conteo_ministros_sol.py")
