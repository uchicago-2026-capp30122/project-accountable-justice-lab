import altair as alt
import pandas as pd

def return_ministers_bar_chart(df, selected_year):
    # 1. Asegurar que los datos sean numéricos y filtrar
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0)
    df['year'] = df['year'].astype(str)
    
    data_filtered = df[df['year'] == str(selected_year)].copy()
    
    # Si no hay datos, devolver un chart vacío con un mensaje
    if data_filtered.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No hay datos']})).mark_text().encode(text='msg:N')

    # 2. Definir la gráfica
    chart = (
        alt.Chart(data_filtered)
        .mark_bar(
            cornerRadiusEnd=5,
            height=20  # Grosor de la barra para que se vea bien
        )
        .encode(
            # Forzamos a que el eje X empiece en 0 con scale(zero=True)
            x=alt.X('count:Q', 
                    title="Número de Menciones", 
                    scale=alt.Scale(domainMin=0, zero=True)),
            
            y=alt.Y('minister:N', 
                    sort='-x', 
                    title="Ministro",
                    axis=alt.Axis(labelLimit=300)), # Que no corte los nombres largos
            
            # Color basado en el conteo para que resalten
            color=alt.Color('count:Q', 
                            scale=alt.Scale(scheme='blues'), 
                            legend=None),
            
            tooltip=[
                alt.Tooltip('minister:N', title='Ministro'),
                alt.Tooltip('count:Q', title='Menciones')
            ]
        )
        .properties(
            title=f"Distribución de Menciones - Año {selected_year}",
            width='container', # Se ajusta al ancho de Streamlit
            height=500
        )
    )

    return chart