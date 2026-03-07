import pandas as pd
import subprocess
from pathlib import Path

INPUT_FILE = "data/clean_data/declaraciones/compiled_dataset_filtered.xlsx"
OUT_DIR = Path("data/raw_data/declaraciones/pdf_text")
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_excel(INPUT_FILE, dtype=str)

pdf_col = "hipervinculo"
links = df[pdf_col].fillna("").astype(str)

for idx, url in enumerate(links):
    url = url.strip()
    if not url:
        continue

    pdf_path = OUT_DIR / f"{idx}.pdf"
    txt_path = OUT_DIR / f"{idx}.txt"

    # Download pdf
    subprocess.run(["curl", "-L", "-sS", url, "-o", str(pdf_path)], check=True)

    # Convert pdf -> text with layout
    subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=True)

print("Ready. PDFs and TXTs saved in:", OUT_DIR)
