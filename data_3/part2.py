import pandas as pd
import subprocess
from pathlib import Path

INPUT_FILE = "compiled_dataset_filtered.xlsx"
OUT_DIR = Path("pdf_text")
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_excel(INPUT_FILE)

# Looks for "hipervinculo" column
pdf_col = "hipervinculo"
links = df[pdf_col].fillna("").astype(str)

# Loops through every url
for i, url in enumerate(links):
    url = url.strip()
    if not url:
        continue

    # Naming
    pdf_path = OUT_DIR / f"{i}.pdf"
    txt_path = OUT_DIR / f"{i}.txt"

    #Creo que estas cosas las podría correr directamente del terminal, pero así me aseguro que quede en el código. 
    #Es como un equivalente a correr esto en el terminal: pdftotext -layout input.pdf output.txt
    # Curl es para descargar cosas de internet/ -L es para follow redirects
    
    # 1) Downloads PDF with curl 
    subprocess.run(["curl","-sS", url, "-o", str(pdf_path)], check=True)
    # 2) Converts to layout text (depends on poppler)
    subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=True)

print("Ready. Texts in", OUT_DIR)
