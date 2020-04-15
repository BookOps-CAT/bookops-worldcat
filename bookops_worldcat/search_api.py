# -*- coding: utf-8 -*-

import requests


from .constant import ORD_MAP, KEY_MAP, SRU_INDICES
from ._session import WorldcatSession


class SearchSession(WorldcatSession):
    """ 
    Worlcat Search API wrapper session. Inherits requests.Session methods.
    Requests to Search API endpoints return records encoded as MARC XML. This webservice
    has a limit of 50k queries a day as a rolling 24 hours limit.

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
        if credentials == "":
            raise ValueError("Argument credentials cannot be an empty string.")

        self.key = credentials
        self.base_url = "http://www.worldcat.org/webservices/catalog/"
        self.headers.update({"Accept": "application/xml"})
        self.payload = {"wskey": self.key}

    def _lookup_isbn_url(self, isbn):
        return f"{self.base_url}content/isbn/{isbn}"

    def _lookup_issn_url(self, issn):
        return f"{self.base_url}content/issn/{issn}"

    def _lookup_oclc_number_url(self, oclc_number):
        return f"{self.base_url}content/{oclc_number}"

    def _lookup_standard_number_url(self, std_number):
        return f"{self.base_url}content/sn/{std_number}"

    def _prepare_request_payload(self, **kwargs):
        prepped_payload = self.payload.copy()
        for key, value in kwargs.items():
            if value:
                prepped_payload[key] = value
        return prepped_payload

    def _prepare_sort_keys(self, sort_keys):
        mapped_sort = []
        for key, order in sort_keys:
            mapped_sort.append(f"{KEY_MAP[key]}{ORD_MAP[order]}")
        return " ".join(mapped_sort)

    def _prepare_sru_query_str(self, query):
        # include better error handling of invalid queries in the future
        # verify query argument
        if type(query) is not str:
            raise TypeError("Argument query cannot be None.")
        if query == "":
            raise ValueError("Argument query cannot be an empty string.")
        if "srw." not in query:
            raise ValueError("Seach query syntax error.")
        if query.count("&") > 0 or query.count("|") > 0 or query.count("<>") > 0:
            query = (
                query.replace("=", "+=+")
                .replace("&", "+and+")
                .replace("|", "+OR+")
                .replace("<>", "+NOT+")
            )
        return query

    def _sru_query_url(self, query):
        return f"{self.base_url}search/sru?query={query}"

    def lookup_isbn(self, isbn=None, service_level="default"):
        """
        Service returns a matching record with the highest holdings in Worldcat.
        Records retrieved in the MARCXML format.
        Args:
            isbn: str,              International Standard Book Number
            service_level: str,     'default' or 'full', see details here:
                                    https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html
        Retruns:
            response: requests.Response object
        """

        if type(isbn) is not str:
            raise TypeError("Argument isbn cannot be None.")
        if isbn == "":
            raise ValueError("Argument isbn cannot be an empty string.")
        if type(service_level) is not str:
            raise TypeError("Invalid type of argument service_level.")
        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")

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
        Retruns:
            response: requests.Response object
        """

        if type(issn) is not str:
            raise TypeError("Argument issn cannot be None.")
        if issn == "":
            raise ValueError("Argument issn cannot be an empty string.")
        if type(service_level) is not str:
            raise TypeError("Invalid type of service_level argument.")
        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")

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
        Retruns:
            response: requests.Response object
        """

        if type(oclc_number) is not str:
            raise TypeError("Argument oclc_number must be a string.")
        if oclc_number == "":
            raise ValueError("Arguemnts oclc_number cannot be empty string.")
        if not oclc_number.isdigit():
            raise ValueError("Argument oclc_number must include only numbers.")
        if type(service_level) is not str:
            raise TypeError("Invalid type of argument service_level.")
        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")

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
        Retruns:
            response: requests.Response object
        """

        if type(std_number) is not str:
            raise TypeError("Argument std_number must be a string.")
        if std_number == "":
            raise ValueError("Argument std_number cannot be an empty string.")
        if type(service_level) is not str:
            raise TypeError("Argumetn service_level must be a string.")
        if service_level not in ["default", "full"]:
            raise ValueError("Invalid value of service_level argument passed.")

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

    def sru_query(
        self,
        query=None,
        start_record=1,
        maximum_records=10,
        sort_keys=[("relevance", "descending")],
        frbr_grouping="off",
        service_level="default",
    ):
        """
        Args:
            query: str                  query string that can include multiple clauses;
                                        use OCLC indexes found here:
                                        
                                        use double quotes, and following operators:
                                        & = AND, | - OR, <> - NOT; do not use spaces
                                        between clauses;
                                        examples:
                                            srw.bn="9781680502404"
                                            srw.au="mann"&srw.ti="faustus"
                                            srw.kw="civil war"&(srw.su="antietam"|srw.su="sharpsburg")
            start_record: int           the starting position of the result set
            maximum_records: int        the maximum number of records to return in a
                                        single request, top limit is 100
            sort_keys: list of tuples   specifies how the result is sorted; accepts
                                        multiple sort_keys; each sort_key consits of
                                        a tuple (sortKey, order), for example:
                                        ('relevance', 'ascending'); supported sort_keys:
                                            - relevance (only descending)
                                            - title
                                            - author
                                            - date
                                            - library_count
                                            - score

            frbr_grouping: str          turns on or off FRBR grouping;
                                        options: 'on', 'off'
            service_level: str          fuller or abreviated records,
                                        options: 'default', 'full';
                                        more here:
                                        https://www.oclc.org/developer/develop/web-services/worldcat-search-api/service-levels.en.html 
        Returns:
            response: requests.Response object
        """

        # verify start_record argument
        if type(start_record) != int:
            raise TypeError("Argument start_record must be an integer.")
        if start_record <= 0:
            raise ValueError("Arguments start_record must be equal or greater than 1.")

        # verify maximum_records argument
        if type(maximum_records) != int:
            raise TypeError("Argument maximum_records must be an integer.")
        if maximum_records == 0 or maximum_records > 100:
            raise ValueError(
                "Agrument maxiumum_records accepts integers between 1 and 100."
            )

        # verify sort_keys argument
        if type(sort_keys) is not list:
            raise TypeError(
                "Argument sort_key must be a list of tuples consisting of two strings."
            )
        if sort_keys == []:
            raise ValueError(
                "Argument sort_key must be a list of tuples consisting of two strings."
            )
        for args in sort_keys:
            if type(args) is not tuple:
                raise TypeError(
                    "Argument sort_key must be a list of tuples consisting of "
                    "two strings."
                )
            for a in args:
                if type(a) is not str:
                    raise TypeError(
                        "Argument sort_key must be a list of tuples consisting of "
                        "two strings."
                    )
                if a == "":
                    raise ValueError(
                        "Argument sort_key must be a list of tuples consisting of "
                        "two not empty strings."
                    )
            if len(args) != 2:
                raise ValueError("Too many arguments passed in sort_keys tuple.")
            if args[0] not in [
                "relevance",
                "title",
                "author",
                "date",
                "library_count",
                "score",
            ]:
                raise ValueError("Invalid first element of sort_keys argument.")
            if args[1] not in ["ascending", "descending"]:
                raise ValueError("Ivalid second element of sort_keys argument.")
            if args[0] == "relevance" and args[1] != "descending":
                raise ValueError(
                    "Key 'relevance' must be sorted as 'descending' "
                    "in sort_keys argumeent."
                )

        # verify frbr_grouping argument
        if type(frbr_grouping) is not str:
            raise TypeError("Argument frbr_grouping cannot be None.")
        if frbr_grouping not in ["on", "off"]:
            raise ValueError("Invalid argument frbr_grouping.")

        # verify frbr_grouping and sort_keys interaction
        # behavior per OCLC Search API docs
        if frbr_grouping == "on" and len(sort_keys) > 1:
            raise ValueError(
                "Invalid combination of arguments. "
                "Multiple sort_keys only works if frbr_grouping=off."
            )

        # verify service_level argument
        if type(service_level) is not str:
            raise TypeError("Invalid type of argument service_level.")
        if service_level == "":
            raise ValueError("Argument service_level cannot be an empty string.")
        if service_level not in ["default", "full"]:
            raise ValueError("Invalid argument service_level.")

        # prepare payload
        sort_keys = self._prepare_sort_keys(sort_keys)
        payload = {
            "maximumRecords": maximum_records,
            "startRecord": start_record,
            "sortKeys": sort_keys,
            "frbrGrouping": frbr_grouping,
            "servicelevel": service_level,
        }

        # prep
        payload = self._prepare_request_payload(**payload)
        prepped_query = self._prepare_sru_query_str(query)
        url = self._sru_query_url(prepped_query)

        # send reques
        try:
            response = self.get(url, params=payload, timeout=self.timeout)
            return response

        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
