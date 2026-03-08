import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/total_inmuebles.xlsx")

def build_inmuebles_table(inmuebles_df):
    """
    Build table removing duplicate properties and selecting relevant columns.
    """

    inmuebles_table = (
        inmuebles_df
        .drop_duplicates(
            subset=[
                "nombre",
                "primer_apellido",
                "superficie_construccion_m2",
                "valor_adquisicion_mxn"
            ]
        )
        [["nombre", "primer_apellido", "superficie_construccion_m2", "valor_adquisicion_mxn"]]
        .reset_index(drop=True)
    )

    return inmuebles_table