import pandas as pd
import subprocess
import shutil
from pathlib import Path

INPUT_FILE = "compiled_dataset_filtrado.xlsx"
OUT_DIR = Path("pdf_text")
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_excel(INPUT_FILE)

#Looks for hipervinculo column
pdf_col = [c for c in df.columns if "HIPERVINCULO" in str(c).upper()][0]
links = df[pdf_col].fillna("").astype(str)

for i, url in enumerate(links):
    url = url.strip()
    if not url:
        continue

    pdf_path = OUT_DIR / f"{i}.pdf"
    txt_path = OUT_DIR / f"{i}.txt"

    try:
        print("Procesando:", i)

        # 1) Descargar PDF con curl (silencioso, sigue redirects, falla si HTTP error)
        subprocess.run(
            ["curl", "-L", "-sS", "-f", url, "-o", str(pdf_path)],
            check=True
        )

        # 2) Convertir a texto con layout
        subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
            check=True
        )

    except subprocess.CalledProcessError as e:
        print("Error en fila", i, e)
        # si quedó un pdf corrupto a medio bajar, bórralo
        if pdf_path.exists() and pdf_path.stat().st_size < 200:
            pdf_path.unlink(missing_ok=True)

print("Listo. Textos en:", OUT_DIR)
