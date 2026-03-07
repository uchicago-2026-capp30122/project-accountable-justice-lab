import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")

print(df.head())
print(df)

#Highest education_level

cols = ["nombre", "primer_apellido", "segundo_apellido", "edu_highest_level"]

edu_por_persona = (
    df[cols]
    .drop_duplicates()
)

print(edu_por_persona)