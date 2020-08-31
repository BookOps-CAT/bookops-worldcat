# -*- coding: utf-8 -*-

"""
Shared utilities
"""


def verify_oclc_number(oclc_number):
    """Verifies a valid looking OCLC number is passed to a request"""
    if oclc_number is None:
        raise TypeError("Argument 'oclc_number' is missing.")
    elif type(oclc_number) is not str:
        raise TypeError("Argument 'oclc_number' must be a string.")
    elif not oclc_number.isdigit():
        raise ValueError("Argument 'oclc_number' must include only digits.")
    else:
        pass
