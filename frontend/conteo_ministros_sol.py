import csv
import unicodedata
from pathlib import Path
from collections import defaultdict

DEFAULT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"
OUTPUT_CSV = "todos_los_ministros_timeseries.csv"

# scjn members per year 
INTEGRACION_POR_ANIO = {
    "2017": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "José Ramón Cossío Díaz", "Margarita Beatriz Luna Ramos", "José Fernando Franco González Salas", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Eduardo Medina Mora", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández"],
    "2018": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "José Ramón Cossío Díaz", "Margarita Beatriz Luna Ramos", "José Fernando Franco González Salas", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Eduardo Medina Mora", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández"],
    "2019": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "José Fernando Franco González Salas", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2020": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "José Fernando Franco González Salas", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2021": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2022": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2023": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "Arturo Zaldívar Lelo de Larrea", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2024": ["Luis María Aguilar Morales", "Alfredo Gutiérrez Ortiz Mena", "Juan Luis González Alcántara Carrancá", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "Lenia Batres Guadarrama", "Jorge Mario Pardo Rebolledo", "Javier Laynez Potisek", "Alberto Pérez Dayán", "Norma Lucía Piña Hernández", "Margarita Ríos Farjat"],
    "2025": ["Hugo Aguilar Ortiz", "Lenia Batres Guadarrama", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "María Estela Ríos González", "Sara Irene Herrerías Guerra", "Giovanni Azael Figueroa Mejía", "Irving Espinosa Betanzo", "Arístides Rodrigo Guerrero García"],
    "2026": ["Hugo Aguilar Ortiz", "Lenia Batres Guadarrama", "Yasmín Esquivel Mossa", "Loretta Ortiz Ahlf", "María Estela Ríos González", "Sara Irene Herrerías Guerra", "Giovanni Azael Figueroa Mejía", "Irving Espinosa Betanzo", "Arístides Rodrigo Guerrero García"]
}

def jaro_winkler(s1, s2):
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2: return 1.0
    len1, len2 = len(s1), len(s2)
    max_dist = max(len1, len2) // 2 - 1
    match = 0
    hash_s1, hash_s2 = [0] * len1, [0] * len2
    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = hash_s2[j] = 1
                match += 1
                break
    if match == 0: return 0.0
    t = 0
    point = 0
    for i in range(len1):
        if hash_s1[i]:
            while hash_s2[point] == 0: point += 1
            if s1[i] != s2[point]: t += 1
            point += 1
    t //= 2
    jaro = (1/3) * (match/len1 + match/len2 + (match - t)/match)
    p, l = 0.1, 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]: l += 1
        else: break
    return jaro + (l * p * (1 - jaro))

def normalize_text(text):
    if not text: return ""
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    for char in ".,?!():;\"'¿¡": text = text.replace(char, " ")
    return " ".join(text.split())

def is_mentioning(text, target_name):
    normalized_target = normalize_text(target_name)
    if normalized_target in text: return True
    target_parts = normalized_target.split()
    words = text.split()
    for part in target_parts:
        # avoid "de", "n", "i" in last names 
        if len(part) < 4: continue 
        for word in words:
            if jaro_winkler(word, part) >= 0.85: return True
    return False

def run_count():
    # start counter because we also need to know if they appear 0 times
    conteos = defaultdict(lambda: defaultdict(int))
    
    print(f"Iniciando conteo en {DEFAULT_CSV}...")
    
    with open(DEFAULT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("year")
            if year not in INTEGRACION_POR_ANIO: continue
            
            clean_text = normalize_text(f"{row.get('DescripcionSolicitud', '')}")
            
            # MAIN FILTER!! solo busca los ministros que corresponden a ESE año
            ministros_del_anio = INTEGRACION_POR_ANIO[year]
            for min_name in ministros_del_anio:
                if is_mentioning(clean_text, min_name):
                    conteos[min_name][year] += 1

    print(f"Guardando resultados en {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "minister", "count"])
        # minister in the supreme court in that year
        for yr, lista_ministros in INTEGRACION_POR_ANIO.items():
            for min_name in lista_ministros:
                cuenta = conteos[min_name].get(yr, 0)
                writer.writerow([yr, min_name, cuenta])
    print("¡Listo!")

if __name__ == "__main__":
    run_count()