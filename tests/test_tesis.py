from pathlib import Path
import sys
import pytest

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from cleaning_and_processing.tesis.utils_tesis import get_ministro, simplify_materia


def test_get_ministro():
    """
    Check function that extracts the name of the justice that drafted the ruling

    Example used: 2030679

    """

    precedentes = "Amparo en revisión 576/2024. 9 de abril de 2025. Cinco votos de las Ministras y los Ministros Jorge Mario Pardo Rebolledo, Juan Luis González Alcántara Carrancá, quien está con el sentido, pero se separa de los párrafos noventa y uno, noventa y cuatro, noventa y seis al noventa y nueve y ciento nueve, y formuló voto concurrente, Ana Margarita Ríos Farjat, Alfredo Gutiérrez Ortiz Mena, quien está con el sentido, pero se separa de todas las consideraciones y formuló voto concurrente y Loretta Ortiz Ahlf. Ponente: Ana Margarita Ríos Farjat. Secretaria: Irlanda Denisse Ávalos Núñez.\r\n\r\nTesis de jurisprudencia 113/2025 (11a.). Aprobada por la Primera Sala de este Alto Tribunal, en sesión privada de veinticinco de junio de dos mil veinticinco."

    ministro = get_ministro(precedentes)

    assert ministro == "ana margarita ríos farjat"


def test_simplify_materia():
    """
    Check function that extracts the first materia (subject) found in a list
    of subjects for a given tesis.

    Example used: tesis 2031119

    """
    materias = "[Civil, Constitucional]"
    main_materia = simplify_materia(materias)
    assert main_materia == "Civil"
