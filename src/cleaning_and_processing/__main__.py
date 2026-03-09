from .tesis.join_tesis import join_tesis_sources
from .sentencias.join_sentencias import join_sentencias_sources
from .solicitudes.ngrams_datos import main as main_ngrams
from .solicitudes.conteo_ministros_sol import run_count
from .solicitudes.clean_solicitudes import main as main_clean


def cleaning_solicitudes():
    main_clean()
    run_count()
    main_ngrams()


def cleaning_tesis():
    join_tesis_sources()


def cleaning_sentencias():
    join_sentencias_sources()


if __name__ == "__main__":
    cleaning_solicitudes()
    cleaning_tesis()
    cleaning_sentencias()
