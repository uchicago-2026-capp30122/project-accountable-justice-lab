import json
import pandas as pd
from pathlib import Path

# Folder with JSON files
JSON_DIR = Path("processing/declaraciones/inmuebles_json")

# Output file
OUT_XLSX = Path("processing/declaraciones/total_inmuebles.xlsx")

rows = []

# Loop all jsons in the folder
for json_file in JSON_DIR.glob("*.json"):

    # Read each json file
    data = json.loads(json_file.read_text(encoding="utf-8"))

    # If empty, skip it
    if not data:
        continue

    # Convert to table
    df = pd.DataFrame(data)

    # Add column with file name  
    df["archivo"] = json_file.name

    rows.append(df)

# Merge all data frames in one 
final_df = pd.concat(rows, ignore_index=True)

# Save 
final_df.to_excel(OUT_XLSX, index=False)

print("Ready. Created Excel:", OUT_XLSX)