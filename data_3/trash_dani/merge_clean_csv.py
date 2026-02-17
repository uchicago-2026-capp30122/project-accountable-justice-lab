import pandas as pd
from pathlib import Path
import unicodedata
import re

folder = Path("raw_data")
out_xlsx = Path("compiled_dataset_filtrado.xlsx")

#Columnas por letra Excel: I y X
COL_I = 8   # I = 9th column -> index 8
COL_X = 23  # X = 24th column -> index 23

def norm_text(x) -> str:
    """Normalize text: str, lower, strip, remove accents, collapse spaces."""
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s

dfs = []

for file in sorted(folder.glob("*.csv")):
    print("Reading:", file.name)

    df = None
    for enc in ("utf-8-sig", "cp1252", "latin1"):
        try:
            df = pd.read_csv(file, sep=";", encoding=enc, engine="python")
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise RuntimeError(f"No se pudo leer {file.name}")

    df["source_file"] = file.name
    dfs.append(df)

final_df = pd.concat(dfs, ignore_index=True, sort=False)

# Seguridad: si algún archivo tiene menos columnas de las necesarias, rellena columnas faltantes
max_cols = max(len(df.columns) for df in dfs)
if len(final_df.columns) < max_cols:
    # normalmente no pasa, pero por seguridad
    final_df = final_df.reindex(columns=list(final_df.columns) + [f"_extra_{i}" for i in range(max_cols - len(final_df.columns))])

# Tomar nombres reales de las columnas I y X (según el DataFrame final)
col_i_name = final_df.columns[COL_I] if len(final_df.columns) > COL_I else None
col_x_name = final_df.columns[COL_X] if len(final_df.columns) > COL_X else None

if col_i_name is None or col_x_name is None:
    raise ValueError(f"Tu dataset no tiene suficientes columnas para I ({COL_I+1}) y X ({COL_X+1}).")

print("\nUsando columnas:")
print("I:", col_i_name)
print("X:", col_x_name)

# Filtrar: contiene "ministro" o "ministra" en I o X (normalizado sin acentos)
i_norm = final_df[col_i_name].map(norm_text)
x_norm = final_df[col_x_name].map(norm_text)

mask = (
    i_norm.str.contains(r"\bministr[oa]\b", regex=True, na=False) |
    x_norm.str.contains(r"\bministr[oa]\b", regex=True, na=False)
)

filtered_df = final_df[mask].copy()

print("\nTotal filas antes del filtro:", len(final_df))
print("Total filas después del filtro:", len(filtered_df))

filtered_df.to_excel(out_xlsx, index=False, engine="openpyxl")

print("\nGuardado:", out_xlsx.resolve())
