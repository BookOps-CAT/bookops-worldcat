# -*- coding: utf-8 -*-

"""
Shared utilities module.
"""
import re
from typing import List, Union

from .errors import InvalidOclcNumber


def _str2list(s: str) -> List[str]:
    """Converts str into list - use for list of OCLC numbers"""
    return [n.strip() for n in s.split(",") if n.strip()]


def prep_oclc_number_str(oclcNumber: str) -> str:
    """
    Checks for OCLC prefixes and removes them.

    Args:
        oclcNumber:
            OCLC record number as string

    Returns:
        `oclcNumber` as str

    Raises:
        InvalidOclcNumber: If `oclcNumber` argument is not a str or int.
    """

    if re.match(r"^ocm[0-9]{,8}$", oclcNumber.strip()) or re.match(
        r"^ocn[0-9]{9}$", oclcNumber.strip()
    ):
        oclcNumber = oclcNumber.strip()[3:]
    elif re.match(r"^on[0-9]{10,}$", oclcNumber.strip()):
        oclcNumber = oclcNumber.strip()[2:]
    elif re.match(r"^\(OCoLC\)ocm[0-9]{,8}$", oclcNumber.strip()) or re.match(
        r"^\(OCoLC\)ocn[0-9]{9}$", oclcNumber.strip()
    ):
        oclcNumber = oclcNumber.strip()[10:]
    elif re.match(r"^\(OCoLC\)on[0-9]{10,}$", oclcNumber.strip()):
        oclcNumber = oclcNumber.strip()[9:]
    elif re.match(r"^\(OCoLC\)[0-9]{8,}$", oclcNumber.strip()):
        oclcNumber = oclcNumber.strip()[7:]

    try:
        oclcNumber = str(int(oclcNumber))
        return oclcNumber
    except ValueError:
        raise InvalidOclcNumber("Argument 'oclcNumber' does not look like real OCLC #.")


def verify_oclc_number(oclcNumber: Union[int, str]) -> str:
    """
    Verifies a valid looking OCLC number is passed and normalize it as integer.

    Args:
        oclcNumber:
            OCLC record number as string or integer

    Returns:
        `oclcNumber` as str

    Raises:
        InvalidOclcNumber: If `oclcNumber` argument is not a str or int or is missing.
    """
    if not oclcNumber:
        raise InvalidOclcNumber("Argument 'oclcNumber' is missing.")

    elif isinstance(oclcNumber, int):
        return str(oclcNumber)

    elif isinstance(oclcNumber, str):
        return prep_oclc_number_str(oclcNumber)

    else:
        raise InvalidOclcNumber("Argument 'oclcNumber' is of invalid type.")


def verify_oclc_numbers(
    oclcNumbers: Union[int, str, List[Union[str, int]]]
) -> List[str]:
    """
    Parses and verifies list of oclcNumbers

    Args:
        oclcNumbers:
            List of OCLC control numbers. Control numbers can be integers or strings
            with or without OCLC # prefix. If str, the numbers must be separated
            by commas. If int, only one number will be parsed. Lists may contain strings
            or integers or a combination of both.

    Returns:
        `oclcNumbers` as a list of strings

    Raises:
        InvalidOclcNumber: If `oclcNumbers` argument is not a list, str, or int.
    """
    if isinstance(oclcNumbers, str):
        oclcNumbers_lst = _str2list(oclcNumbers)
    elif isinstance(oclcNumbers, int):
        oclcNumbers_lst = _str2list(str(oclcNumbers))
    elif isinstance(oclcNumbers, list):
        oclcNumbers_lst = oclcNumbers  # type: ignore
    else:
        raise InvalidOclcNumber(
            "Argument 'oclcNumbers' must be a single integer, a list or a "
            "comma separated string of valid OCLC #s."
        )
    if not oclcNumbers_lst:
        raise InvalidOclcNumber(
            "Argument 'oclcNumbers' must be a single integer, a list or a "
            "comma separated string of valid OCLC #s."
        )

    vetted_numbers = [verify_oclc_number(n) for n in oclcNumbers_lst]
    return vetted_numbers
