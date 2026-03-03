import pandas as pd
import json
from pathlib import Path

INPUT_FILE = "frontend/declaraciones/final_variables.xlsx"

OUT_DIR = Path("processing/declaraciones/inmuebles_json")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Convert excel to dataframe 
df = pd.read_excel(INPUT_FILE, dtype=str)

# Variables to be used
json_col = "inmuebles_json"
juez_col = "nombre"
juez_apellido = "primer_apellido"

for idx, row in df.iterrows():
    value = row[json_col]
    nombre = row[juez_col]
    primer_apellido = row[juez_apellido]

    json_path = OUT_DIR / f"{idx}.json"

    # If empty: remove old file
    if pd.isna(value) or not str(value).strip():
        if json_path.exists():
            json_path.unlink()
        continue

    parsed = json.loads(value)

    # Add name of judge in JSON
    if isinstance(parsed, list):
        for item in parsed:
            item["nombre"] = nombre
    else:
        parsed["nombre"] = nombre
    
    if isinstance(parsed, list):
        for item in parsed:
            item["primer_apellido"] = primer_apellido
    else:
        parsed["primer_apellido"] = primer_apellido

    json_path.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

print("Ready. Non-empty JSON files saved in:", OUT_DIR)