import pandas as pd
import re
import subprocess
import shutil
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

INPUT_FILE = "compiled_dataset_with_pdf_words.xlsx"
OUTPUT_FILE = "compiled_dataset_with_remuneracion.xlsx"
LINK_COL = "pdf_link_extracted"   # <- según tu ejemplo

def download_bytes(url: str, timeout: int = 60) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as r:
        return r.read()

def pdftotext_layout(pdf_path: Path, txt_path: Path) -> None:
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("No encuentro 'pdftotext' en PATH. Prueba `which pdftotext`.")
    subprocess.run(
        [exe, "-layout", "-nopgbrk", str(pdf_path), str(txt_path)],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

def _clean_number(num_str: str) -> int:
    # quita separadores tipo "206 948", "206,948", "206.948"
    digits = re.sub(r"\D", "", num_str)
    return int(digits) if digits else None

def extract_remuneracion(text: str):
    t = text.replace("\r\n", "\n").replace("\r", "\n")

    # Aislar apartado 8 si se puede (opcional)
    m8 = re.search(r"\n?\s*8\.\s+INGRESOS.*?(?=\n\s*9\.)", t, flags=re.IGNORECASE | re.DOTALL)
    block = m8.group(0) if m8 else t

    # Busca el encabezado de remuneración
    m = re.search(r"REMUNERACI[ÓO]N\s+MENSUAL\s+NETA.*?(?:CARGO\s+P[ÚU]BLICO)?",
                  block, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None

    # Tomar una ventana de texto después del encabezado (ahí suele estar el monto)
    window = block[m.end(): m.end() + 600]

    # 1) Preferido: número seguido de MXN (MXN puede salir como M X N)
    mxn_pat = r"(?:M\s*X\s*N)"
    m1 = re.search(r"(\d[\d\s,\.]{1,20})\s*" + mxn_pat, window, flags=re.IGNORECASE)
    if m1:
        return _clean_number(m1.group(1))

    # 2) Si NO hay MXN: primer número “grande” (>= 4 dígitos) en las líneas siguientes
    #    (evita capturar '8.' u otros numeritos)
    m2 = re.search(r"\b(\d[\d\s,\.]{3,20})\b", window)
    if m2:
        val = _clean_number(m2.group(1))
        # filtro simple para evitar basuras muy chicas
        if val is not None and val >= 1000:
            return val

    return None

def main():
    df = pd.read_excel(INPUT_FILE)

    if LINK_COL not in df.columns:
        raise ValueError(f"No encuentro la columna '{LINK_COL}'. Columnas: {list(df.columns)[:20]} ...")

    links = df[LINK_COL].fillna("").astype(str)

    remuneraciones = []
    status = []
    txt_len = []
    is_pdf_list = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        for i, url in enumerate(links):
            url = url.strip()
            if not url or url.lower() == "nan":
                remuneraciones.append(None)
                status.append("sin_link")
                txt_len.append(0)
                is_pdf_list.append(False)
                continue

            try:
                data = download_bytes(url)
                is_pdf = data[:4] == b"%PDF"
                is_pdf_list.append(is_pdf)

                if not is_pdf:
                    remuneraciones.append(None)
                    status.append("no_es_pdf")
                    txt_len.append(0)
                    continue

                pdf_path = tmpdir / f"{i}.pdf"
                txt_path = tmpdir / f"{i}.txt"
                pdf_path.write_bytes(data)

                pdftotext_layout(pdf_path, txt_path)
                text = txt_path.read_text(errors="ignore")
                txt_len.append(len(text))

                val = extract_remuneracion(text)
                remuneraciones.append(val)
                status.append("ok" if val is not None else "no_encontro_remuneracion")

            except HTTPError as e:
                remuneraciones.append(None)
                status.append(f"http_{e.code}")
                txt_len.append(0)
                is_pdf_list.append(False)

            except URLError:
                remuneraciones.append(None)
                status.append("url_error")
                txt_len.append(0)
                is_pdf_list.append(False)

            except subprocess.CalledProcessError:
                remuneraciones.append(None)
                status.append("pdftotext_error")
                txt_len.append(0)
                is_pdf_list.append(True)

            except Exception as e:
                remuneraciones.append(None)
                status.append(f"error_{type(e).__name__}")
                txt_len.append(0)
                is_pdf_list.append(False)

    df["remuneracion_mensual_mxn"] = remuneraciones
    df["remuneracion_status"] = status
    df["download_is_pdf"] = is_pdf_list
    df["txt_len"] = txt_len

    df.to_excel(OUTPUT_FILE, index=False)
    print("Listo:", OUTPUT_FILE)
    print(df["remuneracion_status"].value_counts(dropna=False).head(20))

if __name__ == "__main__":
    main()
