from pathlib import Path
import sys
import pytest
import importlib

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

extract_inmuebles_module = importlib.import_module(
    "cleaning_and_processing.declaraciones.extract_inmuebles"
)
sys.modules["extract_inmuebles"] = extract_inmuebles_module

from cleaning_and_processing.declaraciones.extract_inmuebles import (
    find_section_slice as find_section_slice_inmuebles,
    make_empty_inmueble,
    first_value_after,
    start_inmuebles,
    end_inmuebles,
)

from cleaning_and_processing.declaraciones.final_variables import (
    extract_salary_from_text,
    normalize_level,
    extract_education,
    find_section_slice as find_section_slice_education,
)

def test_find_section_slice_inmuebles():
    """
    check if find_section_slice identifies the bienes inmuebles section bounds
    """
    lines = [
        "1. DATOS GENERALES",
        "9. BIENES INMUEBLES",
        "TIPO DE INMUEBLE",
        "CASA",
        "11. VEHICULOS",
    ]
    result = find_section_slice_inmuebles(lines, start_inmuebles, end_inmuebles)
    assert result == (1, 4)


def test_make_empty_inmueble():
    """
    check if make_empty_inmueble creates the expected template
    """
    result = make_empty_inmueble("Casa")
    assert result == {
        "tipo_inmueble": "Casa",
        "titular": None,
        "porcentaje": None,
        "superficie_terreno_m2": None,
        "superficie_construccion_m2": None,
        "forma_adquisicion": None,
        "forma_pago": None,
        "valor_adquisicion_mxn": None,
        "fecha_adquisicion": None,
    }


def test_first_value_after():
    """
    check if first_value_after returns the first valid value after a label
    """
    chunk = [
        "TIPO DE INMUEBLE",
        "",
        "AGREGAR",
        "CASA",
        "TITULAR DEL INMUEBLE",
    ]
    result = first_value_after(chunk, 0, lookahead=5)
    assert result == "CASA"

def test_normalize_level():
    """
    check if normalize_level removes accents and uppercases text
    """
    assert normalize_level("Maestría") == "MAESTRIA"


def test_extract_education_returns_none_when_section_missing():
    """
    check if extract_education returns (None, None) when academic section
    is not present
    """
    text = """
    1. DATOS GENERALES
    2. OTRA COSA
    """
    level, institution = extract_education(text)
    assert level is None
    assert institution is None

def test_extract_salary_from_text_basic():
    """
    check if extract_salary_from_text finds salary in MXN
    """
    text = """
    I. REMUNERACIÓN
    SUELDO MENSUAL
    150000 MXN
    """
    result = extract_salary_from_text(text)
    assert result == 150000