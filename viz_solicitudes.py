import pandas as pd
import altair as alt


df = pd.read_csv("mentions_timeseries.csv")

df['year'] = pd.to_datetime(df['year'], format='%Y')

# Line Chart cada juez
chart = alt.Chart(df).mark_line(
    point=True,      
    color='#2c3e50', 
    strokeWidth=3
).encode(
    x=alt.X('year:T', title='Year'),
    y=alt.Y('count:Q', title='Number of Solicitudes'),
    tooltip=['year:T', 'count:Q'] 
).properties(
    title='Mentions of Minister Over Time (2017-2026)',
    width=700,
    height=400
).interactive() 


chart.save("mentions_viz.html")
print("Visualization created! Open 'mentions_viz.html' in your browser to see it.")