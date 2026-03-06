# Salient tokens

import csv
import argparse
import math
import unicodedata
import csv
from pathlib import Path
from collections import Counter

DEFAULT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"

STOPWORDS = {
    "el","la","los","las","un","una","unos","unas","y","o","u","e","de","del","al","a","en","por", "denominado"
    "para","con","sin","sobre","que","como","cuando","donde","cada","uno","este","esta","quien",
    "se","su","sus","mi","mis","me","te","le","les","lo","nos","no","sí","si","ya","más","menos",
    "muy","tan","también","tampoco","todo","toda","todos","todas","mismo","misma","así","asi",
    "vez","día","dia","año","ano","parte","partes","estos","estas","esos","esas","aquello","aquella",
    "enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre",
    "mes","meses","periodo","lapso","comprendido","durante","actual","pasado","presente","fecha","fechas",
    "http","https","www","com","mx","html","php","aspx","url","sitio","web","enlace","link","archivo","pdf","formatos",
    "imagen","jpg","png","clic","click","adjunto","adjunta","anexo","anexa","descargar",
    "solicitud","solicito","solicita","solicitante","información","informacion","pública","publica","favor","pudieran",
    "ser","ha","he","fue","son","es","unir","hacer","solicitar","atentamente","cordial","saludo","gracias","trasparencia",
    "unidad","acceso","folio","respuesta","oficio","escrito","presentado","mediante","través","traves","medio",
    "proporcione","entregue","haga","llegar","pueda","dar","conocer","copia","copias","versión","version",
    "pública","publica","documento","documentos","expediente","número","numero","registrado","ingresado",
    "scjn","suprema","corte","justicia","nación","nacion","poder","judicial","federal","ley","artículo","articulo",
    "art","fracción","fraccion","inciso","párrafo","parrafo","tesis","jurisprudencia","rubro","sentencia","ejecutoria",
    "amparo","directo","indirecto","revisión","revision","sala","tribunal","colegiado","circuito","asunto","asuntos",
    "acuerdo","resolución","resolucion","votos","voto","ponente","ministro","ministra","secretario","actuaria",
    "[…]","[...]","...","….","señala","señalada","senala","senalada","punto","puntos","inciso","literal","referencia",
    "relación","relacion","respecto","dicho","dicha","mencionada","citada","tal","tales",
    "sujeto", "obligado", "tiene", "tienen", "ser", "son", "fue", "don", "lic", "está", "esta",
    "mexicanos", "mexicano", "mexicana", "peso", "pesos", "dinero", "adquirido", "adquiridos",
    "adquisicion", "cual", "cuales", "quiere", "quisiera", "tipo", "materia", "versaron", 
    "pertenecientes", "dictada", "respectiva", "fueron", "quien", "presenta", "anexo",
    "ejercicio", "posible", "incluyendo", "hayan", "sea", "manera", "tambien", "debidamente",
    "caracter", "respetuosamente", "disponible", "mensualmente", "anual", "mas", "total",
    "millones", "mil", "tomo", "pagina", "paginas", "folio", "modulo", "tramitada", "derivo",
    "tratar", "danar", "otro", "otra", "otros", "otras", "aquellos", "aquellas", 
    "general", "nacional", "social", "universidad", "directora", "director", "escuela",
    "comunicado", "firmado", "emision", "digital", "electronica", "fisica", "empresa",
    "nombre", "persona", "personas", "punto", "sentido", "amplio", "entradas", "salidas",
    "bienes", "entregado", "elementos", "causas", "procesos", "presuntos", "responsables",
    "irregularidades", "administrativas", "ordenadoras", "validez", "mayor", "autorizada",
    "juridica", "unifamiliar", "identificacion", "comparte", "adjunto",
    "www", "http", "https", "mx", "com", "html", "php", "url", "link", '//www', 'proyectado', "el","la","los","las","un","una","unos","unas",
    "y","o","u","e","de","del","al","a","en","por","para","con","sin","sobre", "señor", "señor",
    "que","como","cuando","donde","cada","uno","este","esta","quien","corresponda","contradicción", "criterio", "criterios",
    "solicitud","solicitar","usted","cordial","saludo","enviar", "ponencia", "ponente", "ministro", "ministra", 
    "se","su","sus","mi","mis","tu","tus","me","te","le","les","lo","nos", "numero", "así", "asi",
    "no","sí","si","ya","más","menos","muy","tan","también","tampoco", "toda", "vez", "dia", "lic", "pudieran",
    "solicito","información","informacion","pública","publica","favor", "fue", "ha", "he", "realizado", "tiene",
    "scjn","suprema","corte","justicia","nación","nacion","unidad","transparencia", "amparo", "amparos", 
    "estados", "unidos", "ley", "federal", "código", "codigo", "reglamento", "constitucion", "constitución",
    "buenas", "tardes", "sujeto", "obligado", "han", "sido", "¿cual", "hacer", "llegar", "tal", "motivo", 
    "medio", "presente", "mexicanos", "directo", "indirecto", "materia", "revisión", "revision", "sentencia", "año",
    "semanario", "judicial", "poder", "dirección", "general", "circuito", "número", "expediente", "es", "cual", "¿cuál"
    "legal","hasta","asuntos","tribunal","sala","año","colegiado", "institución" 
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
    Genera output en terminal y guarda CSVs para Streamlit.
    """
    year_docs = {}
    mentions_per_year = Counter() 
    
    print(f"Reading CSV, filtering by {filter_name if filter_name else 'None'}")
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get("year")
            if not year or not year.isdigit() or int(year) < 2017: 
                continue
            raw_text = row.get('DescripcionSolicitud', '')
            clean_text = normalize_text(raw_text)
            
            if len(clean_text) < 10: continue
            
         # filtro 
            if filter_name:
                if is_mentioning(clean_text, filter_name):
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
    
# calc salient tokens
    all_years = list(year_docs.keys())
    num_years = len(all_years)
    ngram_year_counts = {}
    for year, ngrams in year_docs.items():
        for gram in set(ngrams):
            ngram_year_counts[gram] = ngram_year_counts.get(gram, 0) + 1

    minister_data = []

    # CLI
    title = f"SALIENT {n_size}-GRAM THEMES"
    if filter_name: title += f" FOR: {filter_name.upper()}"
    print(f"\n{'YEAR':<6} | {title}")
    print("-" * 100)

    for year in sorted(all_years, key=int):
        ngrams_in_year = year_docs[year]
        if not ngrams_in_year: continue
        
        counts = Counter(ngrams_in_year)
        total = len(ngrams_in_year)
        scores = []
        for gram, count in counts.items():
            tf = count / total
            idf = math.log(num_years / ngram_year_counts[gram]) if num_years > 1 else 1.0
            scores.append((gram, tf * idf, count))
            
        top_themes = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        print(f"{year:<6} | {', '.join([t[0] for t in top_themes])}")
        
        # save for the minister_data set and tables for streamlit
        for gram, score, count in top_themes:
            minister_data.append({
                "year": year,
                "ngram": gram,
                "count": count,
                "score": score
            })
            
    return minister_data

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
