import csv
import argparse
import math
import unicodedata
import csv
from pathlib import Path
from collections import Counter

DEFAULT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"


## Conteo por ano, o sea cuantos salen en cada ministro, en cuantos solicitudes aparence el ministro!!! 

## Tabla TOP 1, TOP 5, TOP 10, por ministro, ngram por ministro (esto loopear con el set) (NO POR AÑO SINO EN TODOS LOS ANOS)
# altair serie tiempo

STOPWORDS = {
    "el","la","los","las","un","una","unos","unas","y","o","u","e","de","del","al","a","en","por",
    "para","con","sin","sobre","que","como","cuando","donde","cada","uno","este","esta","quien",
    "se","su","sus","mi","mis","me","te","le","les","lo","nos","no","sí","si","ya","más","menos",
    "muy","tan","también","tampoco","scjn","suprema","corte","justicia","nación","nacion",
    "solicitud","solicito","información","informacion","pública","publica","favor","año","toda",
    "vez","dia","lic","pudieran","ser","ha","he","fue","son","es","unir","hacer","solicitar",
    "atentamente","cordial","saludo","gracias","mexicanos","unidos","estados","federal","poder",
    "judicial","ejecutoria","sentencia","expediente","número","numero","materia","revisión",
    "amparo","directo","indirecto","sala","tribunal","colegiado","circuito", "solicita", "hago","requiero", 
    "hacer", "llegar", "medio", "presente", "usted", "dar", "pueda", "proporcione", "copia", "asi", "dio", "precedente","version"
}



def jaro_winkler(s1, s2):
    """calc Jaro-Winkler similarity (0.0 to 1.0),
    Zaldivar Saldivar etc, skip accents 
    """
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2: return 1.0
    
    len1, len2 = len(s1), len(s2)
    # max distance characters can be apart to be considered a match 
    max_dist = max(len1, len2) // 2 - 1
    match = 0
    hash_s1 = [0] * len1
    hash_s2 = [0] * len2

    # find matching chars
    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break
    if match == 0: return 0.0

    # find characters in wrong order
    t = 0
    point = 0
    for i in range(len1):
        if hash_s1[i]:
            while hash_s2[point] == 0:
                point += 1
            if s1[i] != s2[point]:
                t += 1
            point += 1
    t //= 2

    # combine into a score 
    # i added extra if there is prefix matching 
    jaro = (1/3) * (match/len1 + match/len2 + (match - t)/match)
    p, l = 0.1, 0 #p constant scaling factor 
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]: l += 1
        else: break
    return jaro + (l * p * (1 - jaro))

def is_mentioning(text, target_name, threshold=0.92):
    """checks if target_name (or parts of it) 
    appears in text via fuzzy match
    eg is a ministers name appears in a folio request"""
    normalized_target = normalize_text(target_name)
    target_parts = normalized_target.split()
    
    # check full name first (simple substring)
    if normalized_target in text:
        return True
    
    # check individual significant parts (like last names)
    words = text.split()
    for part in target_parts:
        if len(part) < 4: continue # skip short words like 'de'
        for word in words:
            if jaro_winkler(word, part) >= threshold:
                return True
    return False

# THIS IS BASICALLY TEXT PROCESSING 

def normalize_text(text):
    """
    clean text by lowercasing, removing accents and striping punctuation
    normalizing things like Constitución to constitucion so same word
    """
    if not text: return ""
    text = text.lower()
    ## this is where accents are removed
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    for char in ".,?!():;\"'¿¡":
        text = text.replace(char, " ")
    return " ".join(text.split())

def get_ngrams(text, n):
    """
    turn text to list of ngrams
    fikters stopwords and words shorter than 3 letters 
    """
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

# MAIN ANALISIS!! 

def analyze_themes(csv_path, n_size, top_k, filter_name=None):
    """
    groups text by year and applies TF-IDF formula for salient tokens.
    includes a time-series counter for the filtered minister/word.
    """
    year_docs = {}
    mentions_per_year = Counter() # This stays here
    
    print(f"Reading CSV! Filtering by: {filter_name if filter_name else 'None'}")
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("year")
            # Ensure we only look at 2017 onwards as requested
            if not year or not year.isdigit() or int(year) < 2017: 
                continue
                
            raw_text = f"{row.get('DescripcionSolicitud', '')} {row.get('OtrosDatos', '')}"
            clean_text = normalize_text(raw_text)
            
            # MINISTER FILTER
            if filter_name:
                if is_mentioning(clean_text, filter_name):
                    # --- THIS IS THE KEY ADDITION ---
                    mentions_per_year[year] += 1 
                else:
                    continue
                
            ngrams = get_ngrams(clean_text, n_size)
            if year not in year_docs:
                year_docs[year] = []
            year_docs[year].extend(ngrams)

    if not year_docs:
        print("No matches found for that filter")
        return
    
    # OUT PUT FOR COUNTER (this we will use for time series graph)
    if filter_name:
        print(f"\n- SOLICITUDES MENTIONING '{filter_name.upper()}' ---")
        # Sorting ensures 2017 comes before 2018, etc.
        for y in sorted(mentions_per_year.keys(), key=int):
            print(f"{y} | {mentions_per_year[y]} solicitudes")
        print("-" * 65)

    # Calculate Global DF 
    all_years = list(year_docs.keys())
    num_years = len(all_years)
    ngram_year_counts = {}
    for year, ngrams in year_docs.items():
        for gram in set(ngrams):
            ngram_year_counts[gram] = ngram_year_counts.get(gram, 0) + 1

    # TF-IDF Output Table
    title = f"SALIENT {n_size}-GRAM THEMES"
    if filter_name: title += f" FOR: {filter_name.upper()}"
    print(f"\n{'YEAR':<6} | {title}")
    print("-" * 100)

    for year in sorted(all_years, key=int):
        ngrams_in_year = year_docs[year]
        if not ngrams_in_year: 
            continue
        
        counts = Counter(ngrams_in_year)
        total = len(ngrams_in_year)
        scores = []
        for gram, count in counts.items():
            tf = count / total
            idf = math.log(num_years / ngram_year_counts[gram]) if num_years > 1 else 1.0
            scores.append((gram, tf * idf))
            
        top_themes = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        print(f"{year:<6} | {', '.join([t[0] for t in top_themes])}")

    # EXTRA PREPARACION DE DATOS PARA SERIE DE TIEMPO ALTAIR
    counts_file = "mentions_timeseries.csv"
    with open(counts_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "count"])  # header
        # csv cronological 
        for y in sorted(mentions_per_year.keys(), key=int):
            writer.writerow([y, mentions_per_year[y]])
            
    print(f"\nTime series saved to: {counts_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("-n", "--ngram-size", type=int, default=2)
    parser.add_argument("-k", "--top", type=int, default=8)
    parser.add_argument("--filter", type=str, help="Minister name to filter by (eg 'Lenia Batres')")
    
    args = parser.parse_args()
    analyze_themes(args.csv, args.ngram_size, args.top, args.filter)

if __name__ == "__main__":
    main()

# uv run salient_tokens_solicitudes.py -n 2
# uv run salient_tokens_solicitudes.py --filter "Zaldivar" -n 2
# uv run salient_tokens_solicitudes.py -n 2 -k 5 ## top 5 results 








# some of the links used 
"""
https://docs.python.org/3/library/unicodedata.html
https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
https://kleinembedded.com/creating-a-python-command-line-tool/


"""
