"""
clean_solicitudes.py
json files are basically broken:
- some records contain quotes inside text fields 
- some have commas that break the format 
- so we cant use json.loads()

This file:
1- reads the json (decode correctly to preserve acentos and ñ)
2- separates each solicitud with folio 
3- gets the fields using regex
4- cleans texts
5 - one output per year + one large with all years
"""
import csv
import re
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "solicitudes"
OUT_DIR = PROJECT_DIR / "clean_output"


# Columns we want for wach year
CORE_FIELDS = [
    "Folio", "FechaSolicitud", "Dependencia", "Estatus", "MedioEntrada",
    "TipoSolicitud", "DescripcionSolicitud", "OtrosDatos", "ArchivosAdjuntos",
    "MedioEntrega", "FechaLimite", "Respuesta", "TextoRespuesta", "FechaRespuesta",
    "FechaSolicitudTermino", "Pais", "Estado", "Municipio", "CodigoPostal",
    "Sector", "Prorroga", "Prevencion", "Disponibilidad", "TipoDerechoARCOP", "Queja",
]

# add an ISO version YYYY-MM-DD to make time analysis easier on pandas
DATE_FIELDS = ["FechaSolicitud", "FechaLimite", "FechaRespuesta", "FechaSolicitudTermino"]
# Yes/No fields (Si/No) where we want a numeric version for furture use
FLAG_FIELDS = ["Prorroga", "Prevencion", "Disponibilidad", "Queja"]


# FIRST FIND INPUT FILES
def find_year_files():
    """
    Find all yearly files named like 'solicitudes2017.JSON' 
    """
    return sorted(DATA_DIR.glob("solicitudes20*.JSON"))

# CLEAN TEXT FOR CSV 
def clean_text(text:str):
    """
    clean a text value so it won't break CSV output
    - Some fields contain weird control characters from exports
    - dont remove acentos or ñ
    """
    if text is None:
        return ""

    text = str(text)
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def parse_date_ddmmyyyy(date_str:str):
    """
    Convert dates like '31/12/2020' to '2020-12-31' (ISO)
    - ISO sorts correctly as strings
    - Easy to group/filter by year/month in pandas
    """
    date_str = (date_str or "").strip()
    if date_str == "":
        return ""
    return datetime.strptime(date_str, "%d/%m/%Y").date().isoformat()

def yes_no_to_bin(flag_str:str):
    """
    Convert "Si"/"Sí" -> 1 and "No" -> 0.
    """
    flag_str = (flag_str or "").strip().lower()
    if flag_str in ("si", "sí"):
        return 1
    if flag_str == "no":
        return 0
    return ""

# DECODE BYTES WITHOUT LOSING ACCENTS!! (mojibake etc)
def decode_bytes_best(raw:bytes):
    """
    Decode the raw file bytes into text without losing spanish characters.
    not errors="ignore" bc it deletes bytes that don't fit UTF-8
    eg. how 'nación' became 'nacin'
    input: bytes
    output: str
    """
    text = raw.decode("utf-8", errors="replace")
    if "�" in text:
        text = raw.decode("cp1252", errors="replace")
    if "�" in text:
        text = raw.decode("latin-1")

    return text


# "PARSE JSON" WITHOUT json.loads()
def split_records(raw_text:str):
    """
    Split the big file into individual "record blocks"
    - not valid JSON because strings can contain quotes
    - gind the beginning of each request by matching:
        {"Folio":"...
    Then we slice from one start position to the next
    input: str
    output: list of strings (texts)
    """
    starts = [m.start() for m in re.finditer(r'\{"Folio"\s*:\s*"', raw_text)]
    records = []

    for i in range(len(starts)):
        start = starts[i]
        if i < len(starts) - 1:
            end = starts[i + 1]
        else:
            end = len(raw_text)
        block = raw_text[start:end].strip()
        block = re.sub(r"\s*,\s*$", "", block)
        block = re.sub(r"\s*\]\s*\}\s*$", "", block)

        records.append(block)

    return records


def build_field_regex(key: str, all_keys: list[str]):
    """
    build a regex that extracts the value for one field inside a record
    - values may contain commas and quotes 
    - so we cant simply stop at the next quote or comma
    So, we capture with (.*?) until we see:
      a comma + a "KNOWN NEXT KEY" OR
      the end of the block
    """
    # all possible keys that could come after this key
    next_keys = [k for k in all_keys if k != key]
    next_keys_alt = "|".join(map(re.escape, next_keys))

    pattern = (
        rf'"{re.escape(key)}"\s*:\s*"(?P<val>.*?)"'
        rf'(?=\s*,\s*"(?:{next_keys_alt})"\s*:|\s*\}}\s*$)'
    )
    return re.compile(pattern, re.DOTALL)

FIELD_REGEX = {}
for key in CORE_FIELDS:
    FIELD_REGEX[key] = build_field_regex(key, CORE_FIELDS)

def parse_record(block:str):
    """
    block is str
    extract all CORE_FIELDS from one record block
    if a field is missing, we return "" so the CSV stays 'rectangular'
    """
    rec = {}
    for key in CORE_FIELDS:
        match = FIELD_REGEX[key].search(block)
        if match:
            rec[key] = match.group("val")
        else:
            rec[key] = ""
    return rec

# NORMALIZE RECORDS (final columns)
def normalize_record(rec: dict, year: int) -> dict:
    """
    final row of csv
    Adds
    - year (from filename)
    - cleaned text versions of each field
    - clean dates
    - clean yes/no 
    """
    out = {"year": year}
    for key in CORE_FIELDS:
        out[key] = clean_text(rec.get(key, ""))
    for key in DATE_FIELDS:
        out[key + "_iso"] = parse_date_ddmmyyyy(out.get(key, ""))
    for key in FLAG_FIELDS:
        out[key + "_bin"] = yes_no_to_bin(out.get(key, ""))
    return out

def write_csv(rows: list[dict], out_path:Path):
    """
    Write rows to a CSV in UTF-8 (it preserves spanish accents and ñ in output)
    parameters: 
    rows - list of dics
    out_path is a path
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["year"] + CORE_FIELDS

    for key in DATE_FIELDS:
        cols.append(key + "_iso")

    for key in FLAG_FIELDS:
        cols.append(key + "_bin")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def main():
    files = find_year_files()
    OUT_DIR.mkdir(exist_ok=True)
    all_rows = []

    for path in files:
        year = int(re.search(r"(20\d{2})", path.name).group(1))
        print("Processing", path.name)

        raw = path.read_bytes()
        text = decode_bytes_best(raw)
        blocks = split_records(text)

        rows = []
        for block in blocks:
            rec = parse_record(block)
            row = normalize_record(rec, year)
            rows.append(row)

        write_csv(rows, OUT_DIR / f"clean_solicitudes_{year}.csv")
        all_rows.extend(rows)
    write_csv(all_rows, OUT_DIR / "clean_solicitudes_2017_2026.csv")
    print("Done")

if __name__ == "__main__":
    main()