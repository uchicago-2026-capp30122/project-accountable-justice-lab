import csv
import argparse
from pathlib import Path
from collections import Counter

DEFAULT_CSV = Path("clean_output") / "clean_solicitudes_2017_2026.csv"

# this basically just counts 
# in the file salient_tokens_solicitudes there is more of a "comparison" analysis
# this uses raw freq (vs salience tf-idf in the other one)

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

# Minister list
# solo se usa cuando corres --minister-breakdown
# tratar de mergear con lista mafer, incluimos apellidos solos??

## AQUI DEBEMOS DE AGREGAR EL NOMBRE SOLO Y EL APELLIDO SOLO,
# TODOS CON Y SIN ACENTOS, LAS 3 VARIANTES DIFERENTES! 
DEFAULT_MINISTERS = [
    "Norma Piña",
    "Javier Laynez",
    "Loretta Ortiz",
    "Yasmín Esquivel",
    "Alfredo Gutiérrez Ortiz Mena",
    "Margarita Ríos-Farjat",
    "Juan Luis González Alcántara",
    "Ana Margarita Ríos Farjat",
    "Arturo Zaldívar",
    "Luis María Aguilar",
    "Alberto Pérez Dayán",
    "Jorge Mario Pardo",
    "Lenia Batres",
]

# TEXT SELECTION
# cols de texto: 
#   DescripcionSolicitud
#   OtrosDatos
#   TextoRespuesta
#   descripcion -> citizen demand
#   respuesta   ->  institutional response
#   all -> full interaction

def pick_text(row, scope):
    desc = row.get("DescripcionSolicitud", "") or ""
    otros = row.get("OtrosDatos", "") or ""
    resp = row.get("TextoRespuesta", "") or ""

    if scope == "descripcion":
        return f"{desc}\n{otros}"
    if scope == "respuesta":
        return resp
    # default combine everything
    return f"{desc}\n{otros}\n{resp}"


# SUBSTRING FILTER
# restrict analysis to rows that contain a specific word or phrase 
# tipo
#   --contains "engrose"
# case-insensitive matching!! 

def passes_filters(text: str, contains: str | None) -> bool:
    if not contains:
        return True
    return contains.lower() in text.lower()


# NGRAM BY YEAR
# 1 Open CSV
# 2 filter rows by year
# can optionally filter by substring
# 4 combine text
# 6 remove stopwords
# 7 generate n-grams and count them 

def ngrams_by_year(csv_path, year, ngram_size, scope, contains=None):

    texts = []

    # Open cleaned dataset
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Filter using numeric year column
            try:
                if int(row.get("year", -1)) != year:
                    continue
            except ValueError:
                continue

            text = pick_text(row, scope)

            # Optional substring filter
            if not passes_filters(text, contains):
                continue

            texts.append(text)

    # Merge all selected text into one big string
    full_text = "\n".join(texts)

    # somme cleaning like pa1
    full_text = full_text.lower()
    full_text = full_text.replace(".", "")
    full_text = full_text.replace(",", "")
    full_text = full_text.replace("?", "")

    words = full_text.split()
    # Remove stopwords
    clean_words = [w for w in words if w not in STOPWORDS]
    # Generate n-grams
    counts = Counter()
    for i in range(len(clean_words) - ngram_size + 1):
        ngram = " ".join(clean_words[i:i+ngram_size])
        counts[ngram] += 1

    return counts



# MINISTER BREAKDOWN 
# no ngrams, this counts how many folios mention each minister 


def minister_breakdown_by_year(csv_path, year, scope, ministers, contains=None):

    counts = Counter()

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                if int(row.get("year", -1)) != year:
                    continue
            except ValueError:
                continue

            text = pick_text(row, scope)

            if not passes_filters(text, contains):
                continue

            text_lc = text.lower()

            for m in ministers:
                if m.lower() in text_lc:
                    counts[m] += 1

    return counts


# CLI kind of like pa1

def main():

    parser = argparse.ArgumentParser()

    # Required arg
    parser.add_argument("year", type=int, help="Year to analyze (e.g. 2024)")

    # Optional arguments
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--scope", choices=["descripcion","respuesta","all"], default="descripcion")
    parser.add_argument("-n","--ngram-size", type=int, default=2)
    parser.add_argument("-t","--top", type=int, default=10)

    parser.add_argument("--contains", type=str, default=None)
    parser.add_argument("--minister", type=str, default=None)

    parser.add_argument("--minister-breakdown", action="store_true")
    parser.add_argument("--minister-list", nargs="*", default=DEFAULT_MINISTERS)

    args = parser.parse_args()

    # if user puts --minister but not --contains then
    # treat minister name as a substring filter
    contains = args.contains
    if args.minister and not contains:
        contains = args.minister

    # MINISTER BREAKDOWN
    if args.minister_breakdown:
        breakdown = minister_breakdown_by_year(
            args.csv,
            args.year,
            args.scope,
            args.minister_list,
            contains=contains)

        print(f"\nMinister breakdown for {args.year} (scope={args.scope}, contains={contains})")
        print("-" * 70)

        if not breakdown:
            print("No matches")
            return

        for name, c in breakdown.most_common():
            print(f"{c:>6}  {name}")
        return

    # REGULAR NGRAM 
    counts = ngrams_by_year(
        args.csv,
        args.year,
        args.ngram_size,
        args.scope,
        contains=contains)

    print(f"\nTop {args.top} {args.ngram_size}-grams for {args.year} (scope={args.scope}, contains={contains})")
    print("-" * 70)

    if not counts:
        print("No matches")
        return

    for gram, count in counts.most_common(args.top):
        print(f"{count:>6}  {gram}")

if __name__ == "__main__":
    main()

# EXAMPLES TO RUN:
# Top bigrams for 2024 descriptions
# uv run ngrams_solicitudes.py 2024

# Top trigrams for 2023 responses
# uv run ngrams_solicitudes.py 2023 --scope respuesta -n 3 -t 25

# Only rows that contain "engrose" (then compute ngrams)
# uv run ngrams_solicitudes.py 2024 --contains "engrose"

# Shortcut: filter by a minister name (same as --contains)
# uv run ngrams_solicitudes.py 2024 --minister "Lenia Batres"

# Breakdown: how many rows mention each minister in 2024
# uv run ngrams_solicitudes.py 2024 --minister-breakdown

# Breakdown but only among rows that mention "viáticos"
# uv run ngrams_solicitudes.py 2024 --minister-breakdown --contains "viáticos"

# Custom minister list 
# uv run ngrams_solicitudes.py 2024 --minister-breakdown --minister-list "Norma Piña" "Loretta Ortiz"