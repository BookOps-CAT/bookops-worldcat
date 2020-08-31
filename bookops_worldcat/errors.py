# -*- coding: utf-8 -*-

"""
bookops_worldcat exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of bookops_worldcat exceptions.
"""


class BookopsWorldcatError(Exception):
    """Base class for exceptions in this module."""

    pass


class TokenRequestError(BookopsWorldcatError):
    """
    Exception raised when WorldCat access token is not obtained
    """

    pass


class InvalidOclcNumber(BookopsWorldcatError):
    """
    Exception raised when an invalid OCLC record number is encountered
    """
