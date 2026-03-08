from pathlib import Path
import sys
import pytest

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from cleaning_and_processing.sentencias.utils_sentencias import (
    clean_file_number,
    get_votacion,
)


def test_clean_file_number():
    """
    Check if function correctly cleans file numbers that were incorrectly
    transformed into dates from historical csv files provided by the
    Supreme Court

    """
    file_number = "Feb-22"

    cleaned_file = clean_file_number(file_number)

    assert cleaned_file == "02/2022"


def test_get_votacion_u():
    """
    Check if function correctly extracts the voting result from a ruling's
    "votacion" field if it's "unanimidad"

    """
    votacion_text_unanimidad = "POR UNANIMIDAD DE CUATRO VOTOS DE LOS SEÑORES MINISTROS LENIA BATRES GUADARRAMA, ALBERTO PÉREZ DAYÁN (PONENTE), YASMÍN ESQUIVEL MOSSA Y PRESIDENTE JAVIER LAYNEZ POTISEK."
    votacion_u = get_votacion(votacion_text_unanimidad)
    assert votacion_u == "unanimidad"


def test_get_votacion_m():
    """
    Check if function correctly extracts the voting result from a ruling's
    "votacion" field if it's "mayoría"

    """

    votacion_text_mayoria = "POR MAYORÍA DE CUATRO VOTOS DE LOS SEÑORES MINISTROS LENIA BATRES GUADARRAMA, ALBERTO PÉREZ DAYÁN (PONENTE), YASMÍN ESQUIVEL MOSSA Y PRESIDENTE JAVIER LAYNEZ POTISEK."
    votacion_m = get_votacion(votacion_text_mayoria)
    assert votacion_m == "mayoría"


def test_get_votacion_i():
    """
    Check if function correctly extracts the voting result from a ruling's
    "votacion" field if it doesn't find 'unanimidad' or 'mayoria' and results
    in "indeterminado".

    """

    votacion_text_indeterminado = "POR CUATRO VOTOS DE LOS SEÑORES MINISTROS LENIA BATRES GUADARRAMA, ALBERTO PÉREZ DAYÁN (PONENTE), YASMÍN ESQUIVEL MOSSA Y PRESIDENTE JAVIER LAYNEZ POTISEK."
    votacion_i = get_votacion(votacion_text_indeterminado)
    assert votacion_i == "indeterminado"
