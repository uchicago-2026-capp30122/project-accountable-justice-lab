# Salient tokens

import csv
import argparse
import math
import unicodedata
import jellyfish
import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CSV = ROOT / "data" / "clean_data" / "solicitudes" / "clean_solicitudes_2017_2026.csv"

STOPWORDS = {
    "el","la","los","las","un","una","unos","unas","y","o","u","e","de","del","al","a","en","por", "denominado",
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
    "buenas", "tardes", "sujeto", "obligado", "han", "sido", "¿cual", "hacer", "llegar", "tal", "motivo", '2000',
    "medio", "presente", "mexicanos", "directo", "indirecto", "materia", "revisión", "revision", "sentencia", "año",
    "semanario", "judicial", "poder", "dirección", "general", "circuito", "número", "expediente", "es", "cual", "¿cuál"
    "legal","hasta","asuntos","tribunal","sala","año","colegiado", "institución", '-el', '2023', '2024', '&#13', '421','422', 'allegados', '1024/1980'
}

def is_mentioning(text, target_name, threshold=0.92):
    """checks if target_name (or parts of it) 
    appears in text via fuzzy match
    eg is a ministers name appears in a folio request"""
    normalized_target = normalize_text(target_name)
    target_parts = normalized_target.split()
    
    # Check full name first
    if normalized_target in text:
        return True
    
    words = text.split()
    for part in target_parts:
        if len(part) < 4: continue
        for word in words:
            if jellyfish.jaro_winkler_similarity(word, part) >= threshold:
                return True
    return False

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

# uv run src/analysis/solicitudes/salient_tokens_solicitudes.py -n 2
# uv run src/analysis/solicitudes/salient_tokens_solicitudes.py --filter "Zaldivar" -n 2
# uv run src/analysis/solicitudes/salient_tokens_solicitudes.py -n 2 -k 5 (top 5 results) 



