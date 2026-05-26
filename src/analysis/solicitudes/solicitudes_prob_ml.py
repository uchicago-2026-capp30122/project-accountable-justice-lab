# código para leer csv y generar el set de features y outcome final
# importar aquí utils y todas las funciones

import pandas as pd
import numpy as np
import csv
from pysentimiento import create_analyzer
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import joblib

analyzer = create_analyzer(task="sentiment", lang="es")


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data" / "viz_data"

SCALER_PATH = DATA_DIR / "scaler.pkl"
ENCODER_PATH = DATA_DIR / "encoder.pkl"
COLUMNS_PATH = DATA_DIR / "columns.pkl"

scaler = joblib.load(SCALER_PATH)
encoder = joblib.load(ENCODER_PATH)
feature_cols = joblib.load(COLUMNS_PATH)

SAMPLE_CSV = BASE_DIR / "respuestas_formulario.csv"


RESPUESTA_CSV = DATA_DIR / "test_checar.csv"
COEF_CSV = DATA_DIR / "logistic_coefficients.csv"


medio_entrada_dict = {
    "electrónica": "electronica",
    "manual": "manual",
    "dispositivo móvil": "dispositivo_movil",
}

tipo_solicitud_dict = {
    "Información pública": "informacion_publica",
    "Datos Personales": "datos_personales",
}


categorical_columns = [
    "month",
    "medio_entrada",
    "tipo_solicitud",
    "medio_entrega_cat",
    "sentiment",
]


def create_sample() -> pd.DataFrame:
    """

    Create feature dataset

    ver cómo va a llegar el forms

    descripcion solicitud
    medio entrada
    medio entrega
    informacion vs. datos personales

    """

    data = pd.read_csv(SAMPLE_CSV)
    descripcion_solicitud = data["contenido_solicitud"].iloc[0]

    year = datetime.now().year

    features_dict = {
        "medio_entrada": medio_entrada_dict[data["medio_entrada"].iloc[0]],
        "tipo_solicitud": tipo_solicitud_dict[data["tipo_solicitud"].iloc[0]],
        "medio_entrega_cat": categorize_medio_entrega(data["medio_entrega"].iloc[0]),
        "solicitud_len": len(descripcion_solicitud),
        "expediente": check_expediente_existance(descripcion_solicitud),
        "controversial": check_controversial_existance(descripcion_solicitud),
        "month": datetime.now().month,
        "post2024": post2024(year),
        "sentiment": return_sentiment(descripcion_solicitud),
    }

    sample = pd.DataFrame([features_dict])
    sample["solicitud_len"] = scaler.transform(sample[["solicitud_len"]])
    for category in categorical_columns:
        sample = pd.get_dummies(sample, columns=[category], dtype=float)

    sample = sample.reindex(columns=feature_cols, fill_value=0.0)

    sample = sample.drop(columns=["prorroga", "prevencion"])

    sample.to_csv(RESPUESTA_CSV)

    return sample


def return_prediction():

    sample = create_sample()
    coefs = pd.read_csv(COEF_CSV, index_col=0)

    intercept = coefs["intercept"].values[0]
    coef_weights = coefs.drop(columns="intercept")

    shared_cols = sample.columns.intersection(coef_weights.columns)
    features_aligned = sample[shared_cols]
    coefs_aligned = coef_weights[shared_cols]

    # Compute log-odds and probability
    log_odds = (features_aligned.values * coefs_aligned.values).sum(axis=1) + intercept
    probability = 1 / (1 + np.exp(-log_odds))
    prediction = (probability >= 0.5).astype(int)

    # print(f"Log-odds:    {log_odds[0]:.4f}")
    # print(f"Probability: {probability[0]:.4f}")
    # print(f"Prediction:  {prediction[0]}")

    return probability, prediction


## Helper functions to convert and create features from original database


entrega_virtual = [
    "Entrega por Internet en la PNT",
    "Electrónico a través del Sistema de Solicitudes de Acceso a la Información de la PNT",
    "Cualquier otro medio incluido los electrónicos",
    "Correo electrónico",
    "Electrónico a través del sistema de solicitudes de acceso la información de la PNT",
    "Medio electrónico aportado por el solicitante",
]
entrega_presencial = [
    "Cualquier otro medio incluido los electrónicos (CD, DVD, USB)",
    "Consulta directa en la Unidad de Transparencia",
    "Copia Simple",
    "Copia Certificada",
    "Copia certificada",
    "Consulta directa",
    "Consulta Directa",
    "Archivo electrónico en disco o CD",
    "Verbal",
]

otro = ["No Aplica", "Otro medio"]


respuesta_positiva = [
    "Entrega de información vía Plataforma Nacional de Transparencia (Terminada)",
    "Entrega de información en medio electrónico",
    "Información disponible públicamente (Terminada)",
    "Disposición de la información en consulta directa (Terminada)",
    "La información está disponible públicamente",
    "Disponibilidad de la información",
    "Notificación de envío de información de derechos ARCOP (Terminada)",
    "Notificación de lugar y fecha de entrega (Terminada)",
    "Entrega de información (Procedencia)",
    "Registro del ejercicio de los derechos ARCOP (Terminada)",
    "Respuesta a la entrega de información, sin costo",
]

EXPEDIENTE = [
    "expediente",
    "sentencia",
    "sentencias",
    "ejecutoria",
    "ejecutorias",
    "amparo en revisión",
    "amparo",
    "asunto",
    "determinacion",
    "tesis",
    "engrose",
    "resolución",
    "resolucion",
    "resoluciones",
]

CONTROVERSIAL = [
    "robo",
    "corrupcion",
    "corrupcion",
    "denuncia",
    "droga",
    "alcohol",
    "nepotismo",
    "corrupto",
    "soborno",
    "desvío",
    "desvio",
    "enriquecimiento ilicito",
    "enriquecimiento ilícito",
    "irregularidades",
    "ASF",
    "responsabilidades administrativas",
    "sanción",
    "sancion",
    "sanciones",
    "viáticos",
    "fideicomisos",
    "recursos públicos",
    "recursos publicos",
    "moche",
    "conflicto de interés",
    "conflicto de interes",
    "conflictos de interés",
    "conflictos de interes",
    "tortura",
    "desapariciones",
    "tráfico de influencias",
    "trafico de influencias",
    "abuso de auoridad",
]


def categorize_medio_entrega(text_medio):

    if text_medio in entrega_virtual:
        return "virtual"
    elif text_medio in entrega_presencial:
        return "presencial"
    else:
        return "otro"


def categorize_respuesta(text_medio):

    if text_medio in respuesta_positiva:
        return 1
    else:
        return 0


def post2024(year):
    if year >= 2024:
        return 1
    else:
        return 0


def check_expediente_existance(text):
    for word in EXPEDIENTE:
        if word in text:
            return 1
    return 0


def check_controversial_existance(text):
    for word in CONTROVERSIAL:
        if word in text:
            return 1
    return 0


def return_sentiment(text):
    sent = analyzer.predict(text).probas
    return max(sent, key=sent.get)


if __name__ == "__main__":
    return_prediction()
