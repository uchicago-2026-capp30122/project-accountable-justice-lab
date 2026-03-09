import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")

def build_salary_table(declaraciones_df):
    """
    Build the declarations table showing salary per person.
    """
    
    # Remove rows with missing salary information
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

    # Remove ".xlsx" from file name
    salario_por_persona["source_file"] = salario_por_persona["source_file"].str.replace(".xlsx", "", regex=False)

    salario_por_persona = salario_por_persona.rename(
        columns={
            "nombre": "Nombre (Name)",
            "primer_apellido": "Primer apellido (First lastname)",
            "segundo_apellido": "Segundo apellido (Second lastname)",
            "salary_mxn": "Salario (Salary)",
            "source_file": "Fecha archivo"
        }
    )

    return salario_por_persona