# Salient tokens

import csv
import argparse
import math
import unicodedata
import csv
import pandas as pd
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).parent.parent
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

tesis_data = TESIS_DATA / "tesis_joined_data_scjn.csv"

tesis = pd.read_csv(tesis_data, dtype=str)
tesis_2015 = tesis[tesis["anio"].astype("Int64") >= 2015]


# THIS IS BASICALLY TEXT PROCESSING


def normalize_text(text):
    """
    clean text by lowercasing, removing accents and striping punctuation
    normalizing things like Constitución to constitucion so same word
    """
    if not text:
        return ""
    text = text.lower()
    ## this is where accents are removed
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    for char in ".,?!():;\"'¿¡":
        text = text.replace(char, " ")
    return " ".join(text.split())


def get_ngrams(text, n):
    """
    turn text to list of ngrams
    fikters stopwords and words shorter than 3 letters
    """
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


# MAIN ANALISIS!!


def analyze_themes(csv_path, n_size, top_k, filter_name=None):
    """
    groups text by year and applies TF-IDF formula for salient tokens.
    includes a time-series counter for the filtered minister/word.
    Genera output en terminal y guarda CSVs para Streamlit.
    """
    epoca_docs = {}
    # mentions_per_epoca = Counter()

    #  print(f"Reading CSV, filtering by {filter_name if filter_name else 'None'}")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoca = row.get("epoca")
            if not epoca:
                continue
            raw_text = row.get("Precedentes", "")
            clean_text = normalize_text(raw_text)

            ngrams = get_ngrams(clean_text, n_size)
            if epoca not in epoca_docs:
                epoca_docs[epoca] = []
            epoca_docs[epoca].extend(ngrams)

    # calc salient tokens
    all_epocas = list(epoca_docs.keys())
    num_epocas = len(all_epocas)
    ngram_epoca_counts = {}
    for epoca, ngrams in epoca_docs.items():
        for gram in set(ngrams):
            ngram_epoca_counts[gram] = ngram_epoca_counts.get(gram, 0) + 1

    minister_data = []

    # CLI
    title = f"SALIENT {n_size}-GRAM THEMES"
    if filter_name:
        title += f" FOR: {filter_name.upper()}"
    print(f"\n{'YEAR':<6} | {title}")
    print("-" * 100)

    for epoca in sorted(all_epocas, key=int):
        ngrams_in_epoca = epoca_docs[epoca]
        if not ngrams_in_epoca:
            continue

        counts = Counter(ngrams_in_epoca)
        total = len(ngrams_in_epoca)
        scores = []
        for gram, count in counts.items():
            tf = count / total
            idf = (
                math.log(num_epocas / ngram_epoca_counts[gram])
                if num_epocas > 1
                else 1.0
            )
            scores.append((gram, tf * idf, count))

        top_themes = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        #     print(f"{year:<6} | {', '.join([t[0] for t in top_themes])}")

        # save for the minister_data set and tables for streamlit
        for gram, score, count in top_themes:
            minister_data.append(
                {"epoca": epoca, "ngram": gram, "count": count, "score": score}
            )

    return minister_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("-n", "--ngram-size", type=int, default=2)
    parser.add_argument("-k", "--top", type=int, default=8)
    parser.add_argument(
        "--filter", type=str, help="Minister name to filter by (eg 'Lenia Batres')"
    )

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
