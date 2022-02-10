# -*- coding: utf-8 -*-

"""
Shared utilities module.
"""

from typing import List, Union

from .errors import InvalidOclcNumber


def _str2list(s: str) -> List[str]:
    """Converts str into list - use for list of OCLC numbers"""
    return [n.strip() for n in s.split(",")]


def prep_oclc_number_str(oclcNumber: str) -> str:
    """
    Checks for OCLC prefixes and removes them.

    Args:
        oclcNumber:                OCLC record as string

    Returns:
        oclcNumber as int
    """
    if "ocm" in oclcNumber or "ocn" in oclcNumber:
        oclcNumber = oclcNumber.strip()[3:]
    elif "on" in oclcNumber:
        oclcNumber = oclcNumber.strip()[2:]

    try:
        oclcNumber = str(int(oclcNumber))
        return oclcNumber
    except ValueError:
        raise InvalidOclcNumber("Argument 'oclcNumber' does not look like real OCLC #.")


def verify_oclc_number(oclcNumber: Union[int, str]) -> str:
    """
    Verifies a valid looking OCLC number is passed and normalize it as integer.

    Args:
        oclcNumber:                OCLC record number

    Returns:
        oclcNumber

    """
    if oclcNumber is None:
        raise InvalidOclcNumber("Argument 'oclcNumber' is missing.")

    elif type(oclcNumber) is int:
        return str(oclcNumber)

    elif type(oclcNumber) is str:
        return prep_oclc_number_str(oclcNumber)  # type: ignore

    else:
        raise InvalidOclcNumber("Argument 'oclc_number' is of invalid type.")


def verify_oclc_numbers(oclcNumbers: Union[str, List[Union[str, int]]]) -> List[str]:
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
        oclcNumbers = _str2list(oclcNumbers)  # type: ignore

    if not oclcNumbers or type(oclcNumbers) is not list:
        raise InvalidOclcNumber(
            "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #."
        )

    try:
        vetted_numbers = [str(verify_oclc_number(n)) for n in oclcNumbers]
        return vetted_numbers
    except InvalidOclcNumber:
        raise InvalidOclcNumber("One of passed OCLC #s is invalid.")
