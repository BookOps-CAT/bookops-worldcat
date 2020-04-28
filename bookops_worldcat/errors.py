# -*- coding: utf-8 -*-

"""
overload.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of Overload's exceptions.
"""


class BookopsWorldcatError(Exception):
    """Base class for exceptions in this module."""

    pass


class TokenRequestError(BookopsWorldcatError):
    """
    Exception raised when WorldCat access token is not obtained
    """

    pass
