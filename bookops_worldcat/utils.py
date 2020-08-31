# -*- coding: utf-8 -*-

"""
Shared utilities
"""

from .errors import InvalidOclcNumber


def verify_oclc_number(oclc_number):
    """
    Verifies a valid looking OCLC number is passed to a request and

    Args:
        oclc_number:, int or str    OCLC number

    Returns:
        oclc_number: int

    """
    if type(oclc_number) is int:
        return oclc_number

    elif type(oclc_number) is str:

        # allow oclc numbers as strings with or without prefixes
        if "ocm" in oclc_number or "ocn" in oclc_number:
            oclc_number = oclc_number.strip()[3:]
        elif "on" in oclc_number:
            oclc_number = oclc_number.strip()[2:]
        try:
            oclc_number = int(oclc_number)
            return oclc_number
        except ValueError:
            raise InvalidOclcNumber(
                "Argument 'oclc_number' does not look like real OCLC #."
            )

    elif oclc_number is None:
        raise InvalidOclcNumber("Argument 'oclc_number' is missing.")

    else:
        raise InvalidOclcNumber("Argument 'oclc_number' is of invalid type.")
