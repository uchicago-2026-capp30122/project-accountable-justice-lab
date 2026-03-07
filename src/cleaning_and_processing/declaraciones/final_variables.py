# This script enriches an existing Excel dataset of public declarations by extracting
# additional variables from PDF-to-text files.
# 1) Read the base dataset from an Excel file (INPUT_XLSX).
# 2) For each row in the dataset, load the corresponding text file "{idx}.txt" from TEXT_DIR.
#   - Each txt file is the PDF converted to text (e.g., using pdftotext).
#   - The index `idx` matches the row number in the DataFrame.
# 3) From each text file, extract:
#   - Salary / remuneration in MXN (salary_mxn)
#   - Highest academic level and institution (edu_highest_level, edu_highest_institution)
#   - Real estate assets (Bienes Inmuebles) as JSON (inmuebles_json)
# 4) Write the "new" dataset to OUTPUT_XLSX.


import re
from pathlib import Path
import pandas as pd
import json
from extract_inmuebles import extract_inmuebles

INPUT_XLSX = Path("data/clean_data/declaraciones/compiled_dataset_filtered.xlsx")
TEXT_DIR = Path("data/raw_data/declaraciones/pdf_text")
OUTPUT_XLSX = Path("data/clean_data/declaraciones/final_variables.xlsx")

# Remuneration section

# Remuneration regex, finds number with at least three digits followed by MXN
MXN_RE = re.compile(r"\b(\d{3,})\s*MXN\b", re.IGNORECASE)

# Regex for remuneration section
REMU_RE = re.compile(r"\bI\.\s*REMUNERACI[ÓO]N\b", re.IGNORECASE)


def extract_salary_from_text(text: str) -> int | None:
    """Function to extract remuneration.

    - Split the text into lines.
    - Find the first line that contains the remuneration header.
    - Look at a short window of lines after that header.
    - Search inside that window for the first occurrence of a value like "### MXN".
    - Return it as an integer.
    - If not found, return None.
    """

    # Divide text in a list of lines and eliminate spaces
    lines = [ln.strip() for ln in text.splitlines()]

    # Loop through each line looking for remuneration regex
    for i, ln in enumerate(lines):
        # If line contains header, search lines nearby
        if REMU_RE.search(ln):
            # Nine line window from title downwards
            window = " ".join(lines[i : i + 9])
            # Looks for first ### MXN
            m = MXN_RE.search(window)
            if m:
                return int(m.group(1))
    # If header or amount is not found, return None
    return None

# Academic background section 

# Start of academic background section
start_academic_background = re.compile(
    r"^\s*3\.\s*DATOS\s+CURRICULARES\s+DEL\s+DECLARANTE\b",
    re.IGNORECASE,
)

# End of academic background section
end_academic_background = [
    re.compile(r"^\s*4\.\s*DATOS\s+DEL\s+EMPLEO\b", re.IGNORECASE),
    re.compile(r"^\s*5\.\s*EXPERIENCIA\s+LABORAL\b", re.IGNORECASE),
]

# Dictionary to assign point per academic level, so I can filter highest level
# Higher number = higher education level; I do this because not all PDFs have the higher
# level on the first possible block
rank_per_level = {
    "DOCTORADO": 5,
    "MAESTRIA": 4,
    "ESPECIALIDAD": 3,
    "LICENCIATURA": 2,
    "BACHILLERATO": 1,
    "SECUNDARIA": 0,
    "PRIMARIA": 0,
}

# All possible levels of academic background
level_re = re.compile(
    r"\b(DOCTORADO|MAESTR[ÍI]A|ESPECIALIDAD|LICENCIATURA|BACHILLERATO|SECUNDARIA|PRIMARIA)\b",
    re.IGNORECASE,
)

# Looks for academic institution label
institution_re = re.compile(r"\bINSTITUCI[ÓO]N\s+EDUCATIVA\b", re.IGNORECASE)


def find_section_slice(lines, start_re, end_res):
    """
    Finds start and end boundaries. Scans from top to bottom looking for first 
    line that matches start_re and then goes until it finds any end regex matches.
    """
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


def normalize_level(txt):
    return (
        txt.upper()
        .replace("Í", "I")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Ó", "O")
        .replace("Ú", "U")
    )


def extract_education(text: str):
    """
    Extract the highest education level and its institution from the document.
    1) Slice the education section (Section 3) using the start/end headers.
    2) Search the chunk for occurrences of an education level word (level_re).
    3) Convert the detected level into a normalized form and rank it using rank_per_level.
    4) Keep track of the best/highest level found (highest rank).
    5) Once we know where the best level was found (best_index), search forward
       for the "INSTITUCIÓN EDUCATIVA" label and capture the first value below it.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    sl = find_section_slice(lines, start_academic_background, end_academic_background)
    if not sl:
        return None, None

    start, end = sl
    chunk = [ln for ln in lines[start:end] if ln]

    best_level = None
    best_rank = -1
    best_index = None

    # Find highest level of education. If it finds level, normalize and calculate ranking.
    # if its better than the one before, save. Save position.
    for i, ln in enumerate(chunk):
        m = level_re.search(ln)
        if m:
            lvl = normalize_level(m.group(1))
            r = rank_per_level.get(lvl, -1)
            if r > best_rank:
                best_rank = r
                best_level = lvl
                best_index = i

    # Find institution of best level of education
    institution = None
    if best_index is not None:
        for j in range(best_index, min(best_index + 15, len(chunk))):
            if institution_re.search(chunk[j]):
                for k in range(j + 1, min(j + 7, len(chunk))):
                    val = chunk[k].strip()
                    if val and not institution_re.search(val):
                        institution = val
                        break
                break

    return best_level, institution

# Read database 
df = pd.read_excel(INPUT_XLSX, dtype=str)

# Lists will store extracted values row by row
salaries = []
edu_levels = []
edu_insts = []
inmuebles_json_col = []  


for idx in range(len(df)):
    txt_path = TEXT_DIR / f"{idx}.txt"

    if not txt_path.exists():
        salaries.append(None)
        edu_levels.append(None)
        edu_insts.append(None)
        inmuebles_json_col.append(None)  # <<< AGREGAR AQUÍ (nuevo)
        continue

    text = txt_path.read_text(encoding="utf-8", errors="replace")

    # Extract salary
    salaries.append(extract_salary_from_text(text))

    # Extract education highest level + institution 
    level, inst = extract_education(text)
    edu_levels.append(level)
    edu_insts.append(inst)

    # Extract bienes inmuebles and store as JSON sting
    inm_list = extract_inmuebles(text)
    inmuebles_json_col.append(
        json.dumps(inm_list, ensure_ascii=False) if inm_list else None
    )

df["salary_mxn"] = salaries
df["edu_highest_level"] = edu_levels
df["edu_highest_institution"] = edu_insts
df["inmuebles_json"] = inmuebles_json_col  # <<< ESTA LÍNEA FALTABA


df.to_excel(OUTPUT_XLSX, index=False)

print(
    "Ready:",
    OUTPUT_XLSX,
    "rows:",
    len(df),
    "salaries:",
    pd.Series(salaries).notna().sum(),
    "education:",
    pd.Series(edu_levels).notna().sum(),
    "institution:",
    pd.Series(edu_insts).notna().sum(),
    "inmuebles_json:",
    pd.Series(inmuebles_json_col).notna().sum(),  # <<< AGREGAR AQUÍ (nuevo)
)
