import streamlit as st
import pandas as pd
from viz_solicitudes import return_ministers_bar_chart

# 1. Configuración de la página
st.set_page_config(page_title="Monitor de la Corte", layout="wide")

st.title("⚖️ OJO PIOJO con la Corte")
st.header("¿A qué ministros mencionan más los ciudadanos?")

# 2. Función para cargar datos con caché
@st.cache_data
def get_data():
    # Cargamos el CSV generado por el script de conteo
    return pd.read_csv("todos_los_ministros_timeseries.csv")

try:
    df_counts = get_data()
    # Aseguramos que la columna 'year' se lea como texto para evitar errores de comparación
    df_counts['year'] = df_counts['year'].astype(str)

    # 3. Sidebar para la selección del año
    with st.sidebar:
        st.subheader("Configuración")
        # Obtenemos los años únicos que sí existen en el CSV
        available_years = sorted(df_counts['year'].unique(), reverse=True)
        selected_year = st.selectbox("Selecciona el año a visualizar:", available_years)

    # 4. Filtrar los datos por el año seleccionado
    df_year = df_counts[df_counts['year'] == str(selected_year)]

    # 5. VALIDACIÓN CRUCIAL: Solo intentar graficar si hay datos
    if not df_year.empty and df_year['count'].sum() > 0:
        # Generar la gráfica llamando a tu otro archivo
        chart = return_ministers_bar_chart(df_counts, selected_year)

        # Métrica del ministro más mencionado (Ordenamos de mayor a menor)
        top_row = df_year.sort_values('count', ascending=False).iloc[0]
        
        st.metric(
            label=f"Ministro más mencionado en {selected_year}", 
            value=str(top_row['minister']).title(), 
            delta=f"{int(top_row['count'])} menciones"
        )

        # Mostrar la gráfica de Altair
        st.altair_chart(chart, use_container_width=True)
    else:
        # Si el año existe pero todas las cuentas son 0, o no hay filas:
        st.warning(f"No se encontraron menciones para el año {selected_year} en el archivo de datos.")
        st.info("Sugerencia: Revisa si el script de conteo terminó de procesar correctamente el archivo original.")

except FileNotFoundError:
    st.error("No se encontró 'todos_los_ministros_timeseries.csv'. Primero ejecuta: uv run conteo_ministros_sol.py")
except Exception as e:
    st.error(f"Ocurrió un error inesperado: {e}")