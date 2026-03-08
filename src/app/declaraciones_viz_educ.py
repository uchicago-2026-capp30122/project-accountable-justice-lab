import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")

def build_edu_table(declaraciones_df):
    """
    Build the declarations table showing highest education level per person.
    """
    edu_por_persona = (
        declaraciones_df.groupby(["nombre", "primer_apellido", "segundo_apellido"])[
            "edu_highest_level"
        ]
        .first()
        .reset_index()
    )

    edu_por_persona = edu_por_persona.rename(
        columns={
            "nombre": "Nombre",
            "primer_apellido": "Primer apellido",
            "segundo_apellido": "Segundo apellido",
            "edu_highest_level": "Nivel educativo",
        }
    )

    return edu_por_persona

edu_table = build_edu_table(df)
print(edu_table)

