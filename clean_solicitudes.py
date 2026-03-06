"""
clean_solicitudes.py

json files are basically broken:
- Some records contain unescaped quotes inside text fields (eg. rubros with "...")
- That breaks json.loads().
el problema es que hay unas comas que rompen los json entonces rompe el json file 

No strict JSON parsing, but a more robust way
1) Decode correctly to preserve acentos and ń
2) Split file into records/folios by locating 
--> the start of each request: {"Folio":"..."}
3) Extract each field using regex patterns that stop at the next known key
4) Clean text
5) Output (hice uno por año por si acaso pero el que uso para ngrams es el combinado)
"""

from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "solicitudes"
OUT_DIR = PROJECT_DIR / "clean_output"


# WHAT COLUMNS WE WANT
# fields we expect each request (solicitud) to have
# extract ONLY these keys to make a consistent dataset across years.
CORE_FIELDS = [
    "Folio", "FechaSolicitud", "Dependencia", "Estatus", "MedioEntrada",
    "TipoSolicitud", "DescripcionSolicitud", "OtrosDatos", "ArchivosAdjuntos",
    "MedioEntrega", "FechaLimite", "Respuesta", "TextoRespuesta", "FechaRespuesta",
    "FechaSolicitudTermino", "Pais", "Estado", "Municipio", "CodigoPostal",
    "Sector", "Prorroga", "Prevencion", "Disponibilidad", "TipoDerechoARCOP", "Queja",
]

# These are date fields that arrive as dd/mm/yyyy in the raw exports
# add an ISO version YYYY-MM-DD to make time analysis easier
DATE_FIELDS = ["FechaSolicitud", "FechaLimite", "FechaRespuesta", "FechaSolicitudTermino"]

# maybe we will use these Yes/No fields (Si/No) where we want a numeric version for easy stats
FLAG_FIELDS = ["Prorroga", "Prevencion", "Disponibilidad", "Queja"]


# FIRST FIND INPUT FILES
def find_year_files() -> list[Path]:
    """
    Find all yearly files named like 'solicitudes2017.JSON' 
    """
    return sorted(DATA_DIR.glob("solicitudes20*.JSON"))


# CLEAN TEXT FOR CSV 
def clean_text(text: str) -> str:
    """
    Clean a text value so it won't break CSV output
    - Some fields contain weird control characters from exports
    - dont remove acentos or ñ
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # Normalize line endings so all systems behave the same
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove control characters that can break parsing or display
    # (ASCII control codes except \n)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    # Turn runs of spaces/tabs into one space
    text = re.sub(r"[ \t]+", " ", text)

    # Limit huge newline blocks (keeps text readable)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_date_ddmmyyyy(date_str: str) -> str:
    """
    Convert dates like '31/12/2020' to '2020-12-31' (ISO)
    - ISO sorts correctly as strings
    - Easy to group/filter by year/month in pandas
    If parsing fails, return empty string to avoid crashing
    """
    date_str = (date_str or "").strip()
    if not date_str:
        return ""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return ""


def yes_no_to_bin(flag_str: str):
    """
    Convert "Si"/"Sí" -> 1 and "No" -> 0.

    Why?
    - Makes it trivial to compute % of requests with prórroga, prevención, etc.

    If it's missing/unknown, return "" to keep as blank.
    """
    flag_str = (flag_str or "").strip().lower()
    if flag_str in ("si", "sí"):
        return 1
    if flag_str == "no":
        return 0
    return ""


# STEP 3: DECODE BYTES WITHOUT LOSING ACCENTS!! (mojibake etc)
def decode_bytes_best(raw: bytes) -> str:
    """
    Decode the raw file bytes into text *without losing Spanish characters*.

    Why not errors="ignore"?
    - Because it silently deletes bytes that don't fit UTF-8.
    - That is exactly how 'nación' became 'nacin' (ó got dropped).

    Strategy:
    1) Try UTF-8 (most common standard)
    2) If UTF-8 fails, try CP1252 (common in Windows / government exports)
    3) If that fails, use Latin-1 (never fails; maps bytes 0-255 directly)
    """
    try:
        return raw.decode("utf-8")  # strict decode
    except UnicodeDecodeError:
        pass

    try:
        return raw.decode("cp1252")
    except UnicodeDecodeError:
        pass

    return raw.decode("latin-1")


# STEP 4: "PARSE JSON" WITHOUT json.loads()
def split_records(raw_text: str) -> list[str]:
    """
    Split the big file into individual "record blocks".

    - They are not always valid JSON because strings can contain quotes
    - Find the beginning of each request by matching:
        {"Folio":"...

    Then we slice from one start position to the next
    """
    starts = [m.start() for m in re.finditer(r'\{"Folio"\s*:\s*"', raw_text)]
    if not starts:
        return []

    records: list[str] = []
    for i, st in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(raw_text)
        block = raw_text[st:end].strip()

        # Sometimes the slice ends with commas or array/bracket leftovers
        # Remove trailing comma at end of record
        block = re.sub(r"\s*,\s*$", "", block)
        # Remove closing brackets that belong to outer JSON container
        block = re.sub(r"\s*\]\s*\}\s*$", "", block)

        records.append(block)

    return records


def build_field_regex(key: str, all_keys: list[str]) -> re.Pattern:
    """
    Build a regex that extracts the value for one field inside a record
    - Values may contain commas and quotes (eg. rubros: "AUTONOMÍA...")
    - So we CANNOT simply stop at the next quote or comma

    so we try capture everything lazily (.*?) until we see:
      a comma + a "KNOWN NEXT KEY" OR
      the end of the block

    That way:
    - Internal quotes inside values don't break extraction
    - Commas inside text don't break extraction
    """
    # all possible keys that could come after this key
    next_keys = [k for k in all_keys if k != key]
    next_keys_alt = "|".join(map(re.escape, next_keys))

    pattern = (
        rf'"{re.escape(key)}"\s*:\s*"(?P<val>.*?)"'
        rf'(?=\s*,\s*"(?:{next_keys_alt})"\s*:|\s*\}}\s*$)'
    )
    return re.compile(pattern, re.DOTALL)


# Precompile once (faster than compiling inside the loop for every record?)
FIELD_REGEX = {k: build_field_regex(k, CORE_FIELDS) for k in CORE_FIELDS}


def parse_record(block: str) -> dict:
    """
    Extract all CORE_FIELDS from one record block
    If a field is missing, we return "" so the CSV stays 'rectangular'
    """
    rec: dict[str, str] = {}
    for key, rx in FIELD_REGEX.items():
        m = rx.search(block)
        rec[key] = m.group("val") if m else ""
    return rec

# NORMALIZE RECORDS (final columns)
def normalize_record(rec: dict, year: int) -> dict:
    """
    Produce the final row we will write to CSV

    Adds
    - year (from filename)
    - cleaned text versions of each field
    - *_iso versions of dates
    - *_bin versions of yes/no flags
    """
    out: dict = {"year": year}

    # Clean each raw extracted field
    for k in CORE_FIELDS:
        out[k] = clean_text(rec.get(k, ""))

    # Add ISO date columns
    for k in DATE_FIELDS:
        out[f"{k}_iso"] = parse_date_ddmmyyyy(out.get(k, ""))

    # Add binary flag columns
    for k in FLAG_FIELDS:
        out[f"{k}_bin"] = yes_no_to_bin(out.get(k, ""))

    return out


    # CSV OUTPUT
def write_csv(rows: list[dict], out_path: Path) -> None:
    """
    Write rows to a CSV in UTF-8 (it preserves spanish accents and ñ in output)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        print("No rows to write:", out_path)
        return
    cols = ["year"] + CORE_FIELDS
    cols += [f"{k}_iso" for k in DATE_FIELDS]
    cols += [f"{k}_bin" for k in FLAG_FIELDS]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  DONE W/: {out_path.name} ({len(rows)} rows)")

 # MAIN
def main():
    print("Reading JSON files from", DATA_DIR)

    files = find_year_files()
    print(f"Found {len(files)} files\n")

    OUT_DIR.mkdir(exist_ok=True)

    all_rows: list[dict] = []
    per_year_counts: dict[int, int] = {}

    for path in files:
        # Extract year from filename (e.g solicitudes2017.JSON -> 2017)
        m = re.search(r"(20\d{2})", path.name)
        year = int(m.group(1)) if m else -1

        print(f"Processing: {path.name}")

        # read raw byte (worked for acentos and spanish)
        raw = path.read_bytes()

        # decode correctly (preserves accents, no need to dropping bytes
        text = decode_bytes_best(raw)

        # one block per folio/solicitud
        blocks = split_records(text)
        print(f"  -> Record blocks found: {len(blocks)}")
        if not blocks:
            continue

        # extract fields + normalize
        rows: list[dict] = []
        for b in blocks:
            rec = parse_record(b)
            rows.append(normalize_record(rec, year))

        # write per-year output
        per_year_counts[year] = len(rows)
        write_csv(rows, OUT_DIR / f"clean_solicitudes_{year}.csv")

        # add to combined master list
        all_rows.extend(rows)

    # combined output across all years
    print("Processing combined file..")
    combined_path = OUT_DIR / "clean_solicitudes_2017_2026.csv"
    write_csv(all_rows, combined_path)

    print("DONE!!!!!")
    print("Per-year row counts:", dict(sorted(per_year_counts.items())))
    print(f"Total rows combined: {len(all_rows)}")


if __name__ == "__main__":
    main()