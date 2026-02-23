import pandas as pd
import csv
import re


def join_tesis_sources(api_sourcefile, csv_sourcefile):

    api_data = pd.read_csv(api_sourcefile)
    csv_data = pd.read_csv(csv_sourcefile)

    csv_data = csv_data.drop(columns=["Unnamed: 0"])

    joined_tesis = pd.concat([csv_data, api_data], ignore_index=True)
    # Keep año as the only int type column
    joined_tesis["anio"] = joined_tesis["anio"].astype("int64")

    # Modify NA values for anexos
    joined_tesis["anexos"] = joined_tesis["anexos"].fillna("Sin anexos")

    tesis_scjn = filter_by_instancia(
        joined_tesis, "Suprema Corte de Justicia de la Nación"
    )

    tesis_scjn["ministro"] = tesis_scjn["precedentes"].apply(get_ministro)
    tesis_scjn_2015 = filter_by_year(tesis_scjn, 2015)


def get_ministro(precedentes: str):

    pattern = r"Ponente: (.*?)\."
    ministro = re.findall(pattern, precedentes)

    if len(ministro) == 0:
        return "sin datos"
    #  elif len(ministro) > 1:
    #      return "más de uno"
    else:
        return " ".join(ministro)


def filter_by_instancia(tesis, instancia: str):
    # Filter by column instancia
    tesis_instancia = tesis[tesis["instancia"] == instancia]
    return tesis_instancia


def filter_by_year(tesis, year: int):
    # Filter by column anio
    tesis_year = tesis[tesis["anio"] >= year]
    return tesis_year


total_per_year = tesis_scjn_2015.groupby(["epoca", "anio"])["mes"].count()
total_per_year = tesis_scjn.groupby(["epoca", "anio"])["mes"].count()
