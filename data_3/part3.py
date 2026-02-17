# part3_extract_remuneracion.py
import re
from pathlib import Path
import pandas as pd

# Part 1 File
INPUT_XLSX = Path("compiled_dataset_filtered.xlsx")

# Part 2 File
TEXT_DIR = Path("pdf_text")

OUTPUT_XLSX = Path("final.xlsx")

# Regex to find salary like "206948 MXN" / A number with at least 3 digits followed by "MXN"
MXN_RE = re.compile(r"\b(\d{3,})\s*MXN\b", re.IGNORECASE)


def extract_salary_from_text(text: str) -> int | None:
    """
    Looks for salary in section 8. When it finds a line with 'I. REMUNERACIÓN' (mensual/anual/año en curso...)
    looks for first '#### MXN' in that line or next lines.
    """

def extract_salary_from_text(text: str):
    lines = [ln.strip() for ln in text.splitlines()]
    for i, ln in enumerate(lines):
        if re.search(r"\bI\.\s*REMUNERACI[ÓO]N\b", ln, re.IGNORECASE):
            window = " ".join(lines[i:i+9])
            m = MXN_RE.search(window)
            if m:
                return int(m.group(1))
    return None

df = pd.read_excel(INPUT_XLSX, dtype=str)

salaries = []
for idx in range(len(df)):
    txt_path = TEXT_DIR / f"{idx}.txt"
    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8", errors="replace")
        salaries.append(extract_salary_from_text(text))
    else:
        salaries.append(None)

df["salaries"] = salaries
df.to_excel(OUTPUT_XLSX, index=False)
print("Listo:", OUTPUT_XLSX)
