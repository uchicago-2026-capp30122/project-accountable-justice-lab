import pandas as pd
import json
from pathlib import Path


BASE_DIR = Path(__file__).parent

SENTENCIAS_DIR = BASE_DIR / "sentencias_data"


def test_correct_load(filename):

    # Check that json loaded correctly. this will be a test

    # filename to check: tesis_scjn_2015
    with open(SENTENCIAS_DIR / "sentencias_historical.json") as t:
        sentencias_json = json.load(t)

    assert len(sentencias_json) == 104077
