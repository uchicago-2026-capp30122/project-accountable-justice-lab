from pathlib import Path
import pandas as pd
import re

# Must match your setup
INPUT_XLSX = Path("data/clean_data/declaraciones/compiled_dataset_filtered.xlsx")
TEXT_DIR = Path("pdf_text")
xs
COMMON_TYPES = {"CASA","DEPARTAMENTO","TERRENO","LOCAL","OFICINA","BODEGA","RANCHO","PARCELA"}

start_inmuebles = re.compile(r"^\s*(9|10)\.\s*BIENES\s+INMUEBLES\b.*", re.IGNORECASE)
end_inmuebles = [
    re.compile(r"^\s*11\.\s*VEH[ÍI]CULOS\b", re.IGNORECASE),
    re.compile(r"^\s*12\.\s*BIENES\s+MUEBLES\b", re.IGNORECASE),
    re.compile(r"^\s*13\.\s*INVERSIONES\b", re.IGNORECASE),
]
tipo_inmueble_re = re.compile(r"\bTIPO\s+DE\s+INMUEBLE\b", re.IGNORECASE)

def find_section_slice(lines, start_re, end_res):
    start_idx = None
    for i, ln in enumerate(lines):
        if start_re.search(ln):
            start_idx = i
            break
    if start_idx is None:
        return None
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if any(er.search(lines[j]) for er in end_res):
            end_idx = j
            break
    return start_idx, end_idx

df = pd.read_excel(INPUT_XLSX, dtype=str)

rows_with_fallback = []
rows_with_section_but_no_tipo_label = []

for idx in range(len(df)):
    txt_path = TEXT_DIR / f"{idx}.txt"
    if not txt_path.exists():
        continue

    text = txt_path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.strip() for ln in text.splitlines()]
    sl = find_section_slice(lines, start_inmuebles, end_inmuebles)
    if not sl:
        continue

    start, end = sl
    chunk = [ln for ln in lines[start:end] if ln]

    has_tipo_label = any(tipo_inmueble_re.search(ln) for ln in chunk)
    if not has_tipo_label:
        rows_with_section_but_no_tipo_label.append(idx)

    # simulate the condition: we see a COMMON_TYPE before ever seeing the label
    seen_label = False
    fallback_hit = False
    for ln in chunk:
        if tipo_inmueble_re.search(ln):
            seen_label = True
        if (not seen_label) and (ln.upper() in COMMON_TYPES):
            fallback_hit = True
            break

    if fallback_hit:
        rows_with_fallback.append(idx)

print("Rows where fallback (type without label) happens:", rows_with_fallback)
print("Rows where inmueble section exists but NO 'TIPO DE INMUEBLE' label:", rows_with_section_but_no_tipo_label)