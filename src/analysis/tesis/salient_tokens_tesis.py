# Salient tokens

import csv
import argparse
import math
import unicodedata
import csv
import re
import pandas as pd
from pathlib import Path
from collections import Counter
from .datatypes import STOPWORDS


BASE_DIR = Path(__file__).resolve().parents[3]
TESIS_DATA = BASE_DIR / "data" / "clean_data" / "tesis_data"

tesis_data_file = TESIS_DATA / "tesis_joined_data_scjn.csv"

ORDER = [
    "Quinta Época",
    "Sexta Época",
    "Séptima Época",
    "Octava Época",
    "Novena Época",
    "Décima Época",
    "Undécima Época",
    "Duodécima Época",
]


def normalize_text(text):
    """
    Clean text by lowercasing, removing accents and striping punctuation
    normalizing words like Constitución to constitucion be understood as the
    same word.

    Inputs:
        text(str): string of text that needs to be nromalized.
    Returns:
        normalized text
    """
    if not text:
        return ""
    text = text.lower()
    # this is where accents are removed
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    for char in "[]-.,?!():;\"'¿¡":
        text = text.replace(char, " ")
    return " ".join(text.split())


def get_ngrams(text, n):
    """
    Turn text to list of ngrams. And remove stop words, numbers and letters
    shorter than 3 letters
    fikters stopwords and words shorter than 3 letters
    """
    words = [
        w
        for w in re.findall(r"[a-záéíóúüñ]+", text)
        if w not in STOPWORDS and len(w) > 2
    ]

    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def analyze_themes(filename=tesis_data_file, n_size=1, top_k=10):
    """
    Groups text by year and applies TF-IDF formula for salient tokens.


    """
    epoca_docs = {}

    # Read filename and create epoch dictionary. Adding the ngrams to the epoch
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoca = row.get("epoca")
            if not epoca:
                continue
            raw_text = row.get("rubro", "")
            clean_text = normalize_text(raw_text)

            ngrams = get_ngrams(clean_text, n_size)
            if epoca not in epoca_docs:
                epoca_docs[epoca] = []
            epoca_docs[epoca].extend(ngrams)

    # Calculate salient tokens
    all_epocas = list(epoca_docs.keys())
    num_epocas = len(all_epocas)
    ngram_epoca_counts = {}
    for epoca, ngrams in epoca_docs.items():
        for gram in set(ngrams):
            # Add number of mentions for that ngram
            ngram_epoca_counts[gram] = ngram_epoca_counts.get(gram, 0) + 1

    epoca_data = []

    # Total counts for that ngram in a given epoch
    for epoca in all_epocas:
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

        for gram, score, count in top_themes:
            epoca_data.append(
                {"epoca": epoca, "ngram": gram, "count": count, "score": score}
            )

    # Convert to dataframe
    ngrams_df = pd.DataFrame(epoca_data)
    ngrams_df["epoca"] = pd.Categorical(
        ngrams_df["epoca"], categories=ORDER, ordered=True
    )
    return ngrams_df.sort_values(by="epoca")


def main_ngrams():

    # By default calculate ngrams in the tesis data file
    epoca_ngrams = analyze_themes(tesis_data_file)

    return epoca_ngrams


if __name__ == "__main__":
    main_ngrams()
