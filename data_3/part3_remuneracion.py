# part3_extract_remuneracion.py
import re
from pathlib import Path
import pandas as pd

#Part 1 File
INPUT_XLSX = Path("compiled_dataset_filtrado.xlsx")   

#Part 2 File
TEXT_DIR = Path("pdf_text")          
                
OUTPUT_XLSX = Path("compiled_dataset_con_remuneracion.xlsx")

#Regex to find salary like "206948 MXN"
MXN_RE = re.compile(r"\b(\d{3,})\s*MXN\b", re.IGNORECASE)


def extraer_remuneracion_desde_texto(texto: str) -> int | None:
    """
    Looks for salary in section 8. When it fins a line with 'I. REMUNERACIÓN' (mensual/anual/año en curso...)
    looks for first '#### MXN' in that line or next lines. 
    """
    
    #Divides text in lines and strip to eliminate spaces
    lines = [ln.strip() for ln in texto.splitlines()]

    # Encontrar la primera ocurrencia del header de remuneración (sección 8)
    for i, ln in enumerate(lines):
        if re.search(r"\bI\.\s*REMUNERACI[ÓO]N\b", ln, re.IGNORECASE):
            # Buscar monto en una ventana cercana (misma línea + siguientes 8 líneas)
            window = " ".join(lines[i:i+9])
            m = MXN_RE.search(window)
            if m:
                return int(m.group(1))

def main():
    df = pd.read_excel(INPUT_XLSX, dtype=str)

    remuneraciones = []
    errores = 0

    for idx in range(len(df)):
        txt_path = TEXT_DIR / f"{idx}.txt"
        if not txt_path.exists():
            remuneraciones.append(None)
            continue

        try:
            texto = txt_path.read_text(encoding="utf-8", errors="replace")
            val = extraer_remuneracion_desde_texto(texto)
            remuneraciones.append(val)
        except Exception as e:
            errores += 1
            print(f"Error leyendo/procesando {txt_path.name}: {e}")
            remuneraciones.append(None)

    df["remuneracion"] = remuneraciones

    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"Listo: {OUTPUT_XLSX} (errores de lectura: {errores})")

if __name__ == "__main__":
    main()
