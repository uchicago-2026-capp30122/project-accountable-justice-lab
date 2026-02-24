# This module extracts structured information about real estate assets ("Bienes Inmuebles")
# from a PDF converted to plain text. We try to extract section titled
# "9. BIENES INMUEBLES" or "10. BIENES INMUEBLES"
# The goal of this parser is to:
    # 1. Locate that section within the full document text.
    # 2. Identify each individual property block.
    # 3. Extract structured attributes for each property.
    # 4. Return a list of dictionaries (one per property), or None if the section
    # does not exist or contains no usable information.

import re

# Start of "Inmueble" section (some are section 9 and others section 10)
start_inmuebles = re.compile(
    r"^\s*(9|10)\.\s*BIENES\s+INMUEBLES\b.*",
    re.IGNORECASE,
)

# End of section (it might be any of this options)
end_inmuebles = [
    re.compile(r"^\s*11\.\s*VEH[ÍI]CULOS\b", re.IGNORECASE),
    re.compile(r"^\s*12\.\s*BIENES\s+MUEBLES\b", re.IGNORECASE),
    re.compile(r"^\s*13\.\s*INVERSIONES\b", re.IGNORECASE),
]

# Regex for lables inside inmuebles section. They allow flexible spacing and
# optional accents.
tipo_inmueble_re = re.compile(r"\bTIPO\s+DE\s+INMUEBLE\b", re.IGNORECASE)
titular_re = re.compile(r"\bTITULAR\s+DEL\s+INMUEBLE\b", re.IGNORECASE)
forma_adq_re = re.compile(r"\bFORMA\s+DE\s+ADQUISICI[ÓO]N\b", re.IGNORECASE)
forma_pago_re = re.compile(r"\bFORMA\s+DE\s+PAGO\b", re.IGNORECASE)
valor_adq_re = re.compile(r"\bVALOR\s+DE\s+ADQUISICI[ÓO]N\b", re.IGNORECASE)
fecha_adq_re = re.compile(r"\bFECHA\s+DE\s+ADQUISICI[ÓO]N\b", re.IGNORECASE)
pct_re = re.compile(r"\b(\d{1,3})\s*%\b")
m2_re = re.compile(r"\b(\d{1,5})\s*m2\b", re.IGNORECASE)
date_re = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
mxn_amount_re = re.compile(r"\b(\d{3,})\s*MXN\b", re.IGNORECASE)

# Common property types
COMMON_TYPES = {
    "CASA",
    "DEPARTAMENTO",
    "TERRENO",
    "LOCAL",
    "OFICINA",
    "BODEGA",
    "RANCHO",
    "PARCELA",
}


def find_section_slice(lines, start_re, end_res):
    """Find the start and end indices of a section in a list of lines. Returns
    tuple start_re,end_re and None if the section is not found."""
    
    # Identify first occurrence of section start
    start_idx = None
    for i, ln in enumerate(lines):
        # Checks if line contains the start header.
        if start_re.search(ln):
            start_idx = i
            break
        
    # When inmueble section does not exist
    if start_idx is None:
        return None

    # To find end index
    end_idx = len(lines)  
    for j in range(start_idx + 1, len(lines)):
        if any(er.search(lines[j]) for er in end_res):
            end_idx = j
            break

    return start_idx, end_idx


def make_empty_inmueble(tipo):
    """
    Creates a dictionary template for each property. All start with None and will
    be filled as parsing progresses. 
    """
    return {
        "tipo_inmueble": tipo,
        "titular": None,
        "porcentaje": None,
        "superficie_terreno_m2": None,
        "superficie_construccion_m2": None,
        "forma_adquisicion": None,
        "forma_pago": None,
        "valor_adquisicion_mxn": None,
        "fecha_adquisicion": None,
    }


def first_value_after(chunk, idx_label, lookahead=6):
    """
    Find value after label. Since it usually appears in the next few lines, 
    this function uses the lookahead and returns the first candidate that is
    valid. 
    """
    for j in range(idx_label + 1, min(idx_label + 1 + lookahead, len(chunk))):
        cand = chunk[j].strip()
        
        # Skip empty lines
        if not cand:
            continue
        if any(
            rx.search(cand)
            for rx in [
                tipo_inmueble_re,
                titular_re,
                forma_adq_re,
                forma_pago_re,
                valor_adq_re,
                fecha_adq_re,
            ]
        ):
            continue
        if cand.upper() in {"AGREGAR", "TIPO DE OPERACIÓN"}:
            continue
        return cand
    return None


def extract_inmuebles(text: str) -> list[dict] | None:
    """
    Extract "Bienes Inmuebles" from declaration text. Identifies inmueble section,
    splits it into property blocks and extracts structured attributes for each
    property.
    Returns None if section doesn't exist or nothing useful is found.
    """
    # Split into cleaned lines
    lines = [ln.strip() for ln in text.splitlines()]
    
    # Find section boundaries
    sl = find_section_slice(lines, start_inmuebles, end_inmuebles)
    if not sl:
        return None

    start, end = sl

    # Extract only inmbueble section and remove empty lines
    chunk = [ln for ln in lines[start:end] if ln]

    # Final output list
    inmuebles = []
    current = None

    i = 0
    while i < len(chunk):
        ln = chunk[i]

        # Detect start of new property block
        if tipo_inmueble_re.search(ln):
            tipo = first_value_after(chunk, i, lookahead=6)

            # Close previous block, if any
            if current:
                inmuebles.append(current)

            # Start new property block dictionary
            if tipo:
                tipo_up = tipo.upper()
                if tipo_up in COMMON_TYPES or re.fullmatch(
                    r"[A-ZÁÉÍÓÚÑ ]{3,}", tipo_up
                ):
                    current = make_empty_inmueble(tipo.title())
                else:
                    current = make_empty_inmueble(tipo)
            else:
                current = make_empty_inmueble(None)

            i += 1
            continue

        if current is not None:
            # Titular
            if titular_re.search(ln):
                current["titular"] = (
                    first_value_after(chunk, i, lookahead=6) or current["titular"]
                )

            # Percentage
            mp = pct_re.search(ln)
            if mp and current["porcentaje"] is None:
                current["porcentaje"] = int(mp.group(1))

            # Areas in m2: first -> terreno, second -> construccion
            m2s = m2_re.findall(ln)
            if m2s:
                for v in m2s:
                    val = int(v)
                    if current["superficie_terreno_m2"] is None:
                        current["superficie_terreno_m2"] = val
                    elif current["superficie_construccion_m2"] is None:
                        current["superficie_construccion_m2"] = val

            # Acquisition form
            if forma_adq_re.search(ln):
                current["forma_adquisicion"] = (
                    first_value_after(chunk, i, lookahead=6) or current["forma_adquisicion"]
                )

            # Payment form
            if forma_pago_re.search(ln):
                current["forma_pago"] = (
                    first_value_after(chunk, i, lookahead=6) or current["forma_pago"]
                )

            # Acquisition value
            if valor_adq_re.search(ln):
                window = " ".join(chunk[i : i + 10])
                mv = mxn_amount_re.search(window)
                if mv:
                    current["valor_adquisicion_mxn"] = int(mv.group(1))

            # Acquisition date
            if fecha_adq_re.search(ln):
                window = " ".join(chunk[i : i + 12])
                md = date_re.search(window)
                if md:
                    current["fecha_adquisicion"] = md.group(1)

        i += 1

    if current:
        inmuebles.append(current)

    # Remove fully empty blocks. Keep only blocks that contain at least some meaningful nformation. 
    inmuebles = [
        x
        for x in inmuebles
        if x.get("tipo_inmueble")
        or x.get("valor_adquisicion_mxn")
        or x.get("fecha_adquisicion")
    ]

    return inmuebles or None