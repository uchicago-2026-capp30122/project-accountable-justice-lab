import re
from datetime import datetime as dt

"""
Helper functions used to clean sentencias dataframe
"""


def get_votacion(votacion: str):
    """
    This function extracts the result of the voting for that specific ruling.

    In this dataframe, the voting structure is more standarized so there is no
    need to distinguish between the Supreme Court solving in chambers or en banc.

    Inputs:
        - votacion (str): text refering to the voting on the ruling.

    Returns:
        - outcome (str): outcome of voting

    """

    if votacion == "":
        return "indeterminado"
    else:
        pattern_unanimidad = r"(?i)\bunanimidad\b"
        pattern_mayoria = r"(?i)\bmayor[ií]a\b"
        votacion_unanimidad = re.search(pattern_unanimidad, str(votacion))
        if votacion_unanimidad:
            return "unanimidad"
        else:
            votacion_mayoria = re.search(pattern_mayoria, str(votacion))
            if votacion_mayoria:
                return "mayoría"
            else:
                return "indeterminado"


def remove_missing_dates(date: str):
    """
    This function modifies a date that does not follow a day, month, year structure
    into a general date. This structure implies that the date of the ruling was
    not registered.

    Inputs:
        - date (str): date of ruling.

    Returns:
        - date (str): updated value for strings that don't have a standarized
        date format.

    """

    if date == "00:00.0":
        return "01/01/85"
    elif date == "00:00.3":
        return "01/01/85"
    elif date == "23:12.1":
        return "01/01/85"
    else:
        return date


def clean_file_number(file: str):
    """
    Helper function to edit file numbers that were incorrectly converted to
    dates in original data source. For example, file number 02/2022 was converted
    to 'Feb-22'. This regex looks for strings in specific file number columns
    that contain letters and replaces the date structure to a string with
    corresponding file name. Example: from 'Feb-22' to '02/2022'

    Inputs: file (str): file number in string format.

    Output: file (str): same file number but correctly formatted (i.e. eliminating
                        date format and keeping it in file-like structure)
    """

    # Check if file number starts with a letter
    pattern = r"^[A-Z][a-z]+"
    match = re.search(pattern, file)
    if match:
        # We know the string follows a 'mm-year' format
        format_string = "%b-%y"
        # Extract string as a datetime object
        date_object = dt.strptime(file, format_string)
        # Convert it into a numerical-type date we will consider as file number
        formatted_date = date_object.strftime("%m/%Y")
        return formatted_date
    else:
        # If file starts with number, there is nothing to be done
        return file


def clean_ministro_name(ministro: str):

    return str(ministro.lower().strip())
