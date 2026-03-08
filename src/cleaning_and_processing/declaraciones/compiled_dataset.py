import pandas as pd
from pathlib import Path

BASE_DIR = Path("data")

# Compile all quarterly excels
files = sorted((BASE_DIR/"raw_data"/"declaraciones").glob("q*_20*.xlsx"))
dfs = []

for f in files:
    df = pd.read_excel(f)
    df["source_file"] = f.name
    dfs.append(df)

compiled = pd.concat(dfs, ignore_index=True)

# Save compiled inside data
compiled_path = BASE_DIR /"clean_data"/"declaraciones"/ "compiled_all_quarters.xlsx"
compiled.to_excel(compiled_path, index=False)
print("Compiled:", compiled.shape)

# Filter only judges
col = "puesto_perspectiva_genero"
judges = ["Ministro", "Ministra", "Ministra Presidenta"]

mask = compiled[col].astype(str).str.strip().isin(judges)
df_filtered = compiled[mask].copy()

# Save filtered inside data/declaraciones
filtered_path = BASE_DIR /"clean_data"/"declaraciones"/ "compiled_dataset_filtered.xlsx"
df_filtered.to_excel(filtered_path, index=False)

print("Filtered:", df_filtered.shape)