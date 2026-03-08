from pathlib import Path
import sys
import pytest

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from cleaning_and_processing.solicitudes.clean_solicitudes import (
    clean_text,
    parse_date_ddmmyyyy,
    yes_no_to_bin,
)

from analysis.solicitudes.salient_tokens_solicitudes import (
    normalize_text,
    is_mentioning,
)

def test_clean_text():
    """
    check if clean_text removes control characters, normalizes spaces,
    and keeps spanish accents
    """
    raw_text = "Hola\x07   mundo\r\n\r\n\r\nMéxico"
    cleaned = clean_text(raw_text)

    assert cleaned == "Hola mundo\n\nMéxico"


def test_parse_date_ddmmyyyy():
    """
    check if dates in dd/mm/yyyy format are converted to ISO format
    """
    date_str = "31/12/2020"
    parsed = parse_date_ddmmyyyy(date_str)

    assert parsed == "2020-12-31"


def test_yes_no_to_bin_si():
    """
    check if 'Si' is converted to 1
    """
    assert yes_no_to_bin("Si") == 1


def test_yes_no_to_bin_si_accent():
    """
    check if 'Sí' is converted to 1
    """
    assert yes_no_to_bin("Sí") == 1


def test_normalize_text():
    """
    check if normalize_text lowercases, removes accents,
    and strips punctuation
    """
    text = "Constitución, Nación. ¿Información Pública?"
    normalized = normalize_text(text)

    assert normalized == "constitucion nacion informacion publica"


def test_is_mentioning_exact_name():
    """
    check if is_mentioning detects an exact minister name.
    """
    text = normalize_text("Solicito información sobre Lenia Batres Guadarrama.")
    assert is_mentioning(text, "Lenia Batres Guadarrama") is True


def test_is_mentioning_last_name_only_like_request_text():
    """
    check if fuzzy matching detects a likely minister mention
    when part of the name appears in the text.
    """
    text = normalize_text("Quiero saber los viajes de Zaldivar.")
    assert is_mentioning(text, "Arturo Zaldívar Lelo de Larrea") is True

