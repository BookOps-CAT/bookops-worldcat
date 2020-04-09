# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self, credentials=None):
        requests.Session.__init__(self)

        if not credentials:
            raise AttributeError(
                "WorldcatSession requires WorldcatAccessToken object or WSkey."
            )

        self.timeout = (10, 10)
        self.headers.update({"User-Agent": f"{__title__}/{__version__}"})


class SearchSession(WorldcatSession):
    """ 
    Worlcat Search API wrapper session. Inherits requests.Session methods.
    Requests to Search API endpoints return records encoded as MARC XML. This webservice
    has a limit of 50k queries a day as a rolling 24 hours liimit.

    More about WorlcatSearch API here:
        https://www.oclc.org/developer/develop/web-services/worldcat-search-api.en.html

    Requires only WSkey for authentication (WSKey Lite pattern). More about WSkey Lite
    can be found here:
        https://www.oclc.org/developer/develop/authentication/wskey-lite.en.html
    

    Args:
        credentials: instance of WorldcatAccessToken

    Basic usage:

    >>> session = SearchSession(credentials=key)
    >>> session.lookup_by_isbn('9781680502404')
    <Response [200]>

    or using context manager

    >>> with SearchSession(credentails=key) as session:
    ...     session.lookup_by_isbn('9781680502404')
    <Response [200]>
    """

    def __init__(self, credentials=None):
        WorldcatSession.__init__(self, credentials)

        if type(credentials) is not str:
            raise TypeError("OCLC key (WSkey) can be only a string.")

        self.key = credentials
        self.base_url = "http://www.worldcat.org/webservices/catalog/"
        self.headers.update({"Accept": "application/xml"})
        self.payload = {"wskey": self.key}

    def _prepare_request_payload(self, **kwargs):
        prepped_payload = self.payload.copy()
        for key, value in kwargs.items():
            if value:
                prepped_payload[key] = value
        return prepped_payload

    def _lookup_isbn_url(self, isbn):
        return f"{self.base_url}content/isbn/{isbn}"

    def _lookup_issn_url(self, issn):
        return f"{self.base_url}content/issn/{issn}"

    def _lookup_oclc_number_url(self, oclc_number):
        return f"{self.base_url}content/{oclc_number}"

    def _lookup_standard_number_url(self, std_number):
        return f"{self.base_url}content/sn/{std_number}"

    def lookup_isbn(self, isbn=None, service_level="default"):
        """
        Service returns a matching record with the highest holdings in Worldcat.
        Records retrieved in the MARCXML format.
        Args:
            isbn: str,              International Standard Book Number
            service_level: str,     'default' or 'full', see details here:
                                    https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html
        retruns:
            response: requests.Response object
        """

        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")
        if isbn is None:
            raise TypeError("Argument isbn cannot be None.")

        url = self._lookup_isbn_url(isbn)
        payload = self._prepare_request_payload(servicelevel=service_level)

        # send request
        try:
            response = self.get(url, params=payload, timeout=self.timeout)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def lookup_issn(self, issn=None, service_level="default"):
        """
        Service returns a matching record with the highest holdings in Worldcat.
        Records retrieved in the MARCXML format.
        Args:
            issn: str,              International Standard Serial Number,
                                    example '0000-0019'
            service_level: str,     'default' or 'full', see details here:
                                    https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html
        retruns:
            response: requests.Response object
        """

        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")
        if issn is None:
            raise TypeError("Argument issn cannot be None.")

        url = self._lookup_issn_url(issn)
        payload = self._prepare_request_payload(servicelevel=service_level)

        # send request
        try:
            response = self.get(url, params=payload, timeout=self.timeout)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def lookup_oclc_number(self, oclc_number=None, service_level="default"):
        """
        Service returns a matching record with the highest holdings in Worldcat.
        Records retrieved in the MARCXML format.
        Args:
            oclc_number: str,       OCLC record number without any prefix
            service_level: str,     'default' or 'full', see details here:
                                    https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html
        retruns:
            response: requests.Response object
        """

        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")
        if oclc_number is None:
            raise TypeError("Argument std_number cannot be None.")
        if not oclc_number.isdigit():
            raise ValueError("Argument oclc_number must include only numbers.")

        url = self._lookup_oclc_number_url(oclc_number)
        payload = self._prepare_request_payload(servicelevel=service_level)

        # send request
        try:
            response = self.get(url, params=payload, timeout=self.timeout)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def lookup_standard_number(self, std_number=None, service_level="default"):
        """
        Service returns a matching record with the highest holdings in Worldcat.
        Records retrieved in the MARCXML format.
        Args:
            std_number: str,        one of the standard numbers, example:
                                    publisher number, UPC, etc.
            service_level: str,     'default' or 'full', see details here:
                                    https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html
        retruns:
            response: requests.Response object
        """

        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")
        if std_number is None:
            raise TypeError("Argument std_number cannot be None.")

        url = self._lookup_standard_number_url(std_number)
        payload = self._prepare_request_payload(servicelevel=service_level)

        # send request
        try:
            response = self.get(url, params=payload, timeout=self.timeout)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise


class MetadataSession(WorldcatSession):
    """OCLC Metadata API wrapper session. Inherits requests.Session methods"""

    def __init__(self, credentials=None):
        WorldcatSession.__init__(self, credentials)

        if type(credentials).__name__ != "WorldcatAccessToken":
            raise TypeError("Invalid token object passed in the argument.")

        if credentials.token_str is None:
            raise TypeError(
                "Missing token_str in WorldcatAccessToken object passes as credentials."
            )

        self.base_url = "https://worldcat.org/"
