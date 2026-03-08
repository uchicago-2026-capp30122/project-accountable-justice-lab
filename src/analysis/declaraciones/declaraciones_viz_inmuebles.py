import pandas as pd

df = pd.read_excel("data/clean_data/declaraciones/total_inmuebles.xlsx")

def build_inmuebles_table(inmuebles_df):
    """
    Build table with no duplicate rows.
    """
    
    inmuebles_table = (
        inmuebles_df
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return inmuebles_table
