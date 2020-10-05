# -*- coding: utf-8 -*-

"""
<<<<<<< HEAD
Shared utilities
"""

from .errors import InvalidOclcNumber


def str2list(s):
    return [n.strip() for n in s.split(",")]


def verify_oclc_number(oclcNumber):
=======
Shared utilities module.
"""

from typing import List, Union

from .errors import InvalidOclcNumber


def _parse_error_response(response):
    """
    Parses and formats error responses from OCLC web service

    Args:
        response: requests.Response obj
    """

    response.encoding = "utf-8"
    msg = response.text

    return f"Web service returned {response.status_code} error: {msg}; {response.url}"


def _str2list(s: str) -> List:
    """Converts str into list - use for list of OCLC numbers"""
    return [n.strip() for n in s.split(",")]


def verify_oclc_number(oclcNumber: Union[int, str]) -> int:
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e
    """
    Verifies a valid looking OCLC number is passed to a request and

    Args:
<<<<<<< HEAD
        oclc_number:, int or str    OCLC number

    Returns:
        oclc_number: int
=======
        oclcNumber:                OCLC record number

    Returns:
        oclcNumber
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e

    """
    if oclcNumber is None:
        raise InvalidOclcNumber("Argument 'oclcNumber' is missing.")

    elif type(oclcNumber) is int:
        return oclcNumber

    elif type(oclcNumber) is str:

        # allow oclc numbers as strings with or without prefixes
        if "ocm" in oclcNumber or "ocn" in oclcNumber:
            oclcNumber = oclcNumber.strip()[3:]
        elif "on" in oclcNumber:
            oclcNumber = oclcNumber.strip()[2:]
        try:
            oclcNumber = int(oclcNumber)
            return oclcNumber
        except ValueError:
            raise InvalidOclcNumber(
                "Argument 'oclcNumber' does not look like real OCLC #."
            )
    else:
        raise InvalidOclcNumber("Argument 'oclc_number' is of invalid type.")


<<<<<<< HEAD
def verify_oclc_numbers(oclcNumbers):
=======
def verify_oclc_numbers(oclcNumbers: Union[str, List]) -> List:
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e
    """
    Parses and verifies list of oclcNumbers

    Args:
<<<<<<< HEAD
        oclcNumbers: list or str    list of OCLC control numbers for which holdings
                                    should be set;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
    Returns:
        vetted_numbers: list,       list of vetted oclcNumbers
=======
        oclcNumbers:            list of OCLC control numbers for which holdings
                                should be set;
                                they can be integers or strings with or without
                                OCLC # prefix;
                                if str the numbers must be separated by comma
    Returns:
        vetted_numbers:         list of vetted oclcNumbers
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e
    """

    # change to list if comma separated string
    if type(oclcNumbers) is str:
<<<<<<< HEAD
        oclcNumbers = str2list(oclcNumbers)
=======
        oclcNumbers = _str2list(oclcNumbers)
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e

    if not oclcNumbers or type(oclcNumbers) is not list:
        raise InvalidOclcNumber(
            "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #."
        )

    try:
        vetted_numbers = [str(verify_oclc_number(n)) for n in oclcNumbers]
        return vetted_numbers
    except InvalidOclcNumber:
        raise InvalidOclcNumber("One of passed OCLC #s is invalid.")
<<<<<<< HEAD


def parse_error_response(response):
    """
    Parses and formats error responses from OCLC web service

    Args:
        response: requests.Response obj
    """

    response.encoding = "utf-8"
    msg = response.text

    return f"Web service returned {response.status_code} error: {msg}; {response.url}"
=======
>>>>>>> 6a9b36d3c1c098afa9f695b1d95b1698bffe571e
