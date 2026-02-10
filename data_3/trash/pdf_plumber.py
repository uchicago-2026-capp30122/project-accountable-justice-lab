import pdfplumber
import pandas as pd
import re
from pathlib import Path


PDF_PATH = "data_3/1.pdf"
OUTPUT_DIR = "output"

def extract_full_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(
            page.extract_text()
            for page in pdf.pages
            if page.extract_text()
        )


def extract_section(text, start, end=None):
    if end:
        pattern = rf"{start}(.*?){end}"
    else:
        pattern = rf"{start}(.*)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

# 1. DATOS GENERALES
# -----------------------------
def extract_datos_generales(text):
    section = extract_section(text, r"1\. DATOS GENERALES", r"3\. DATOS CURRICULARES DEL DECLARANTE")

    def find(label):
        m = re.search(label + r"\n+([^\n]+)", section)
        return m.group(1).strip() if m else None

    return {
        "nombre": find(r"NOMBRE\(S\)"),
        "primer_apellido": find(r"PRIMER APELLIDO"),
        "segundo_apellido": find(r"SEGUNDO APELLIDO"),
        "correo": find(r"CORREO ELECTRÓNICO INSTITUCIONAL"),
    }

# 2. EDUCACIÓN (REPETIDA)
# -----------------------------
def extract_educacion(text):
    section = extract_section(text, r"3\. DATOS CURRICULARES DEL DECLARANTE", r"4. DATOS DEL EMPLEO, CARGO O COMISIÓN QUE INICIA")
    blocks = section.split("NIVEL ESTATUS DOCUMENTO OBTENIDO")

    educacion = []

    for block in blocks[1:]:
        nivel = re.search(r"(DOCTORADO|MAESTRÍA|LICENCIATURA)", block)
        institucion = re.search(r"INSTITUCIÓN EDUCATIVA\s+([^\n]+)", block)
        carrera = re.search(r"CARRERA O ÁREA DE CONOCIMIENTO\s+([^\n]+)", block)
        fecha = re.search(r"(\d{2}/\d{2}/\d{4})", block)

        educacion.append({
            "nivel": nivel.group(1) if nivel else None,
            "institucion": institucion.group(1) if institucion else None,
            "carrera": carrera.group(1) if carrera else None,
            "fecha_obtencion": fecha.group(1) if fecha else None,
        })

    return educacion


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    text = extract_full_text(PDF_PATH)

    datos_generales = extract_datos_generales(text)
    educacion = extract_educacion(text)

    pd.DataFrame([datos_generales]).to_csv(f"{OUTPUT_DIR}/datos_generales.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(educacion).to_csv(f"{OUTPUT_DIR}/educacion.csv", index=False, encoding="utf-8-sig")

    print("✅ Extracción completa")
    print("📂 Archivos generados en /output")


if __name__ == "__main__":
    main()
