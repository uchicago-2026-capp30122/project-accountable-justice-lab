import re

"""
Helper functions used to clean tesis dataframe
"""


def get_expediente(precedentes: str):
    """
    This function extracts the file number of the court case. That generally
    follows the structure "number/year".


    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - expediente (str): file number.

    """

    precedentes = precedentes.lower().strip()
    pattern = r"\d+/\d+"
    expediente = re.search(pattern, precedentes)

    if not expediente:
        return "sin datos"
    else:
        return expediente.group(0)


def get_tipo_asunto(precedentes: str):
    """
    This function extracts the type of court case from the precedentes field.
    The type of case is normally mentioned at the strart of the precedentes
    text and is followed by the file number.

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - tipo_asunto (str): type of court case.

    """

    precedentes = precedentes.lower().strip()
    pattern = r"^(.+?)\s+\d+/\d+"
    asunto = re.search(pattern, precedentes)

    if not asunto:
        return "sin datos"
    else:
        return asunto.group(1)


def get_ponente(precedentes: str):
    """
    This function extracts the name of ponente (judge or justice) from a
    text. This function is built according to the general format of the column
    "precedentes", which follows the general rule of stating within the text
    (not necessarily at the beginning) "Ponente: First Middle Last Name".

    This is the same function as get ministro (only for this one we are generalizing
    for tesis beyond the Supreme Court)

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - ponente (str): name of judge that drafted the tesis.

    """

    precedentes = precedentes.lower().strip()
    pattern = (
        r"(?<=ponente:\s)([a-záéíóúüñ]+(?:\s[a-z][\.,]?)*(?:\s[a-záéíóúüñ]+)+)(?=[\.,])"
    )
    noise = r"ministr[o|a]\s|president[e|a]\s|magistrad[o|a]"
    ponente = re.search(pattern, precedentes)

    if not ponente:
        return "sin datos"
    else:
        ponente = ponente.group(1)
        ponente_clean = re.sub(noise, "", ponente)
        return ponente_clean


def get_secretaria(precedentes: str):
    """
    This function extracts the name of secretaria/o (clerk) from a
    text. This function is built according to the general format of the column
    "precedentes", which follows the general rule of stating within the text
    (not necessarily at the beginning) "Secretaria(o): First Middle Last Name".

    This is the same function as get ponente (only for this one we are generalizing
    for tesis beyond the Supreme Court)

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - secretaria (str): name of clerk that drafted the tesis.

    """

    precedentes = precedentes.lower().strip()
    pattern = r"(?:secretaria|secretario|secretarias|secretarios|secretariado):\s([a-záéíóúüñ]+(?:\s[a-z][\.,]?)*(?:\s[a-záéíóúüñ]+)+)(?=[\.,])"
    secretaria = re.search(pattern, precedentes)

    if not secretaria:
        return "sin datos"
    else:
        return secretaria.group(1)


def get_ministro(precedentes: str):
    """
    This function extracts the name of ministro or ministra (justice) from a
    text. This function is built according to the general format of the column
    "precedentes", which follows the general rule of stating within the text
    (not necessarily at the beginning) "Ponente: First Middle Last Name".

    There are some corner cases where typos in middle names do not allow us
    to have a full match. But this only happens with two justices. Because of this
    we added another function "fuzzy_match_ministro" to narrow down unique
    values of justices.

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - ministro (str): name of justice.

    """

    precedentes = precedentes.lower().strip()
    pattern = (
        r"(?<=ponente:\s)([a-záéíóúüñ]+(?:\s[a-z][\.,]?)*(?:\s[a-záéíóúüñ]+)+)(?=[\.,])"
    )
    noise = r"ministr[o|a]\s|president[e|a]\s"
    ministro = re.search(pattern, precedentes)

    if not ministro:
        return "sin datos"
    else:
        ministro = ministro.group(1)
        ministro_clean = re.sub(noise, "", ministro)
        ministro = secondary_match_ministro(ministro_clean)
        return ministro_clean


def secondary_match_ministro(ministro: str):
    """
    This function adds another validation level from the regex obtained in
    "get_ministro" function. Particularly for two edge cases found in the dataset
    related to the ministros "sergio a. valls hernández" and "juan n. silva meza".

    We know this is not a scalable solution but given the total number of
    justices in the dataframe and the years we will analyze their data, this
    solution is more precise than doing a fuzzy match.

    Inputs:
        - ministro (str): name of justice extracted from regex pattern

    Returns:
        - ministro (str): name of justice with secondary processing given
        two edge cases.

    """

    ministro = ministro
    ministro_words = ministro.split()
    if ministro_words[0] == "sergio":
        return "sergio a. valls hernández"
    elif ministro_words[0] == "juan":
        if ministro_words[1] != "luis":
            return "juan n. silva meza"
    else:
        return ministro


def get_votacion_pleno(text: str):
    """
    This function extracts the result of the voting for that specific tesis.
    A tesis can be voted by unanimity or majority. We needed a regex because
    sometimes the text doesn't contain these exact words but rather the count of
    votes.

    Because of this. This function only deals with cases of the Supreme Court
    acting "in banc" and not in chambers.

    The cases where there is not match will be labeled as "indeterminado"
    (undetermined), which could be that the text is empty or the wording is
    too abstract for a direct extraction.

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - outcome (str): outcome of voting

    """

    pattern_unanimidad = r"(?:[U|u]nanimidad | [O|once] votos | [N|n]ueve votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [O|o]cho votos | [S|s]iete votos | [S|s]eis)"
    votacion_unanimidad = re.search(pattern_unanimidad, text)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, text)
        if votacion_mayoria:
            return "mayoría"
        else:
            return "indeterminado"


def get_votacion_salas(text: str):
    """
    This function extracts the result of the voting for that specific tesis.
    A tesis can be voted by unanimity or majority. We needed a regex because
    sometimes the text doesn't contain these exact words but rather the count of
    votes.

    Because of this. This function only deals with cases of the Supreme Court
    acting in chambers and not in banc.

    The cases where there is not match will be labeled as "indeterminado"
    (undetermined), which could be that the text is empty or the wording is
    too abstract for a direct extraction.

    Inputs:
        - precedentes (str): text refering to the precedentes column in a tesis
        dataframe

    Returns:
        - outcome (str): outcome of voting

    """

    pattern_unanimidad = r"(?:[U|u]nanimidad | [C|c]inco votos)"
    pattern_mayoria = r"(?:[M|m]ayoría | [C|c]uatro votos | [T|t]res votos)"
    votacion_unanimidad = re.search(pattern_unanimidad, text)
    if votacion_unanimidad:
        return "unanimidad"
    else:
        votacion_mayoria = re.search(pattern_mayoria, text)
        if votacion_mayoria:
            return "mayoría"
        else:
            return "indeterminado"


def simplify_materia(materias: str):
    """
    This function extracts the first type of subject (materia) related to the
    tesis. Because some tesis have more than one subject, we will only classify
    them with the first one identified.

    Inputs:
        - materias (str): text refering to the materias (subjects) of the tesis.

    Returns:
        - materia (str): first materia identified in the text

    """

    materia_pattern = r"([A-Za-záéíóúÁÉÍÓÚüÜñÑ]+)"
    materia = re.search(materia_pattern, str(materias))
    if materia:
        return materia.group()
    else:
        return ""
