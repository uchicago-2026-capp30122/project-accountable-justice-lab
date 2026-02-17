import pandas as pd

# Load dataset
df = pd.read_excel("compiled_dataset.xlsx")

# Filter column
col = "puesto_perspectiva_genero"

# Only bring judges
filter = df[col].isin(["Ministro", "Ministra", "Ministra Presidenta"])

df_filtered = df[filter]

# Save new excel
df_filtered.to_excel("compiled_dataset_filtered.xlsx", index=False)

print("Filtered compiled dataset:", df_filtered.shape)
