import pandas as pd

TOTAL_MINISTROS = 13

def metrica_completitud_educacion(df1):
    
    id_cols = ["nombre", "primer_apellido", "segundo_apellido"]
    
    ministros_con_educacion = (
        df1.dropna(subset=["edu_highest_level"])[id_cols]
        .drop_duplicates()
        .shape[0]
    )
    
    porcentaje = ministros_con_educacion / TOTAL_MINISTROS
    
    return {
        "total_ministros": TOTAL_MINISTROS,
        "con_educacion_declarada": ministros_con_educacion,
        "porcentaje": porcentaje
    }


def metrica_completitud_inmuebles(df2):
    
    id_cols = ["nombre", "primer_apellido"]
    
    ministros_con_inmueble = (
        df2.dropna(subset=["valor_adquisicion_mxn"])[id_cols]
        .drop_duplicates()
        .shape[0]
    )
    
    porcentaje = ministros_con_inmueble / TOTAL_MINISTROS
    
    return {
        "total_ministros": TOTAL_MINISTROS,
        "con_al_menos_un_inmueble": ministros_con_inmueble,
        "porcentaje": porcentaje
    }
    

##df1 = pd.read_excel("data/clean_data/declaraciones/final_variables.xlsx")
##df2 = pd.read_excel("data/clean_data/declaraciones/total_inmuebles.xlsx")
##
##
##m1 = metrica_completitud_educacion(df1)
##m2 = metrica_completitud_inmuebles(df2)
##
##print(m1)
##print(m2)