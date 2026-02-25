import pandas as pd
import json
from pathlib import Path


BASE_DIR = Path(__file__).parent

TESIS_DIR = BASE_DIR / "tesis_data"


def test_correct_load(filename):

    # Check that json loaded correctly. this will be a test

    # filename to check: tesis_scjn_2015
    with open(TESIS_DIR / "tesis_scjn_2015.json") as t:
        tesis_json_2025 = json.load(t)

    assert len(tesis_json_2015) == 5374
