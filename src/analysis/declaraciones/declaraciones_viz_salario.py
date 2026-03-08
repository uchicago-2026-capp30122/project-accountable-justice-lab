import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")


def build_salary_table(declaraciones_df):
    """
    Build the declarations table showing highest education level per person.
    """
    
    # Remove rows with missing education information
    declaraciones_df = declaraciones_df.dropna(
        subset=["salary_mxn"]
    )
    
    salario_por_persona = (
        declaraciones_df.groupby(["nombre", "primer_apellido", "segundo_apellido"])[
            ["salary_mxn","source_file"]
        ]
        .first()
        .reset_index()
    )

    salario_por_persona = salario_por_persona.rename(
        columns={
            "nombre": "Nombre",
            "primer_apellido": "Primer apellido",
            "segundo_apellido": "Segundo apellido",
            "salary_mxn": "Salario",
            "source_file": "Fecha archivo"
        }
    )

    return salario_por_persona
