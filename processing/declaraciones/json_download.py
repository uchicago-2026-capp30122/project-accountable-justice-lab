import pandas as pd
import json
from pathlib import Path

INPUT_FILE = "frontend/declaraciones/final_variables.xlsx"

OUT_DIR = Path("processing/declaraciones/inmuebles_json")
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(INPUT_FILE, dtype=str)

json_col = "inmuebles_json"

for idx, value in enumerate(df[json_col]):
    json_path = OUT_DIR / f"{idx}.json"

    # If empty → remove old file (so empties don't appear)
    if pd.isna(value) or not str(value).strip():
        if json_path.exists():
            json_path.unlink()
        continue

    # Non-empty → write JSON
    parsed = json.loads(value)
    json_path.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

print("Ready. Non-empty JSON files saved in:", OUT_DIR)