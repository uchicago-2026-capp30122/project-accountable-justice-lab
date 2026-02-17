import pandas as pd
from pathlib import Path

#List of paths were files are
files = sorted(Path("raw_data").glob("q*_20*.xlsx"))

dfs = []
for f in files:
    df = pd.read_excel(f)
    df["source_file"] = f.name   
    dfs.append(df)

compiled = pd.concat(dfs, ignore_index=True)
compiled.to_excel("compiled_all_quarters.xlsx", index=False)

print("Ready:", compiled.shape)