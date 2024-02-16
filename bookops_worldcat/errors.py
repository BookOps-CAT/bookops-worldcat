# -*- coding: utf-8 -*-

"""
This module contains the set of bookops_worldcat exceptions.
"""


class BookopsWorldcatError(Exception):
    """Base class for exceptions in this module."""

    pass


class WorldcatAuthorizationError(BookopsWorldcatError):
    """
    Exception raised when WorldCat access token is not obtained
    """

    pass


class WorldcatSessionError(BookopsWorldcatError):
    """
    Exception raised during WorldCat session
    """

    pass


class WorldcatRequestError(WorldcatSessionError):
    """
    Exceptions raised on HTTP errors returned by web service
    """

    pass


class InvalidOclcNumber(BookopsWorldcatError):
    """
    Exception raised when an invalid OCLC record number is encountered
    """

    pass
