# -*- coding: utf-8 -*-

"""
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
    """
    Verifies a valid looking OCLC number is passed to a request and

    Args:
        oclcNumber:                OCLC record number

    Returns:
        oclcNumber

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


def verify_oclc_numbers(oclcNumbers: Union[str, List]) -> List:
    """
    Parses and verifies list of oclcNumbers

    Args:
        oclcNumbers:            list of OCLC control numbers for which holdings
                                should be set;
                                they can be integers or strings with or without
                                OCLC # prefix;
                                if str the numbers must be separated by comma
    Returns:
        vetted_numbers:         list of vetted oclcNumbers
    """

    # change to list if comma separated string
    if type(oclcNumbers) is str and oclcNumbers != "":
        oclcNumbers = _str2list(oclcNumbers)

    if not oclcNumbers or type(oclcNumbers) is not list:
        raise InvalidOclcNumber(
            "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #."
        )

    try:
        vetted_numbers = [str(verify_oclc_number(n)) for n in oclcNumbers]
        return vetted_numbers
    except InvalidOclcNumber:
        raise InvalidOclcNumber("One of passed OCLC #s is invalid.")
