import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")


def build_edu_table(declaraciones_df):
    """
    Build the declarations table showing highest education level per person.
    """
    
    # Remove rows with missing education information
    declaraciones_df = declaraciones_df.dropna(
        subset=["edu_highest_level", "edu_highest_institution"]
    )
    
    edu_por_persona = (
        declaraciones_df.groupby(["nombre", "primer_apellido", "segundo_apellido"])[
            ["edu_highest_level", "edu_highest_institution"]
        ]
        .first()
        .reset_index()
    )

    edu_por_persona = edu_por_persona.rename(
        columns={
            "nombre": "Nombre (Name)",
            "primer_apellido": "Primer apellido (First lastname)",
            "segundo_apellido": "Segundo apellido (Second lastname)",
            "edu_highest_level": "Mayor nivel educativo alcanzado (Highest academic level achieved)",
            "edu_highest_institution": "Institución académica (Academic institution)"
        }
    )

    return edu_por_persona
