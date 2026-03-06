import altair as alt
import pandas as pd

def return_ministers_bar_chart(df, selected_year):
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0)
    df['year'] = df['year'].astype(str)
    data_filtered = df[df['year'] == str(selected_year)].copy()
    
    # si no hay datos
    if data_filtered.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No hay datos']})).mark_text().encode(text='msg:N')

    # graph 
    chart = (
        alt.Chart(data_filtered)
        .mark_bar(
            cornerRadiusEnd=5,
            height=20  
        )
        .encode(
            # make axis start at 0 not 250 
            x=alt.X('count:Q', 
                    title="Número de Menciones", 
                    scale=alt.Scale(domainMin=0, zero=True)),
            
            y=alt.Y('minister:N', 
                    sort='-x', 
                    title="Ministro",
                    axis=alt.Axis(labelLimit=300)), 
            
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
            width='container',
            height=500
        )
    )

    return chart