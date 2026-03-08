from .ngrams_datos import main as main_ngrams
from .conteo_ministros_sol import run_count
from .clean_solicitudes import main as main_clean


if __name__ == "__main__":
    main_clean()
    run_count()
    main_ngrams()
