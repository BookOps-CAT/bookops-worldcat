# -*- coding: utf-8 -*-

import requests

from ._session import WorldcatSession
from .utils import verify_oclc_number


class MetadataSession(WorldcatSession):
    """OCLC Metadata API wrapper session. Inherits requests.Session methods"""

    def __init__(self, authorization=None, agent=None, timeout=None):
        WorldcatSession.__init__(self, agent=agent, timeout=timeout)

        self.authorization = authorization

        if type(self.authorization).__name__ != "WorldcatAccessToken":
            raise TypeError(
                "Argument 'authorization' must include 'WorldcatAccessToken' obj."
            )

        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _url_base(self):
        return "https://worldcat.org"

    def _url_search_base(self):
        return "https://americas.metadata.api.oclc.org/worldcat/search/v1"

    def _url_member_shared_print_holdings(self):
        base_url = self._url_search_base()
        return f"{base_url}/bibs-retained-holdings"

    def _url_member_general_holdings(self):
        base_url = self._url_search_base()
        return f"{base_url}/bibs-summary-holdings"

    def _url_brief_bib_search(self):
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs"

    def _url_brief_bib_oclc_number(self, oclcNumber):
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclcNumber}"

    def _url_brief_bib_other_editions(self, oclcNumber):
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclcNumber}/other-editions"

    def _url_lhr_control_number(self, controlNumber):
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings/{controlNumber}"

    def _url_lhr_search(self):
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings"

    def _url_lhr_shared_print(self):
        base_url = self._url_search_base()
        return f"{base_url}/retained-holdings"

    def _url_bib_oclc_number(self, oclcNumber):
        base_url = self._url_base()
        return f"{base_url}/bib/data/{oclcNumber}"

    def _url_bib_check_oclc_numbers(self):
        base_url = self._url_base()
        return f"{base_url}/bib/checkcontrolnumbers"

    def _url_bib_holding_libraries(self):
        base_url = self._url_base()
        return f"{base_url}/bib/holdinglibraries"

    def _url_bib_holdings_action(self):
        base_url = self._url_base()
        return f"{base_url}/ih/data"

    def _url_bib_holdings_check(self):
        base_url = self._url_base()
        return f"{base_url}/ih/checkholdings"

    def _url_bib_holdings_batch_action(self):
        base_url = self._url_base()
        return f"{base_url}/ih/datalist"

    def _url_bib_holdings_multi_institution_batch_action(self):
        base_url = self._url_base()
        return f"{base_url}/ih/institutionlist"

    def search_shared_print_holdings(self, hooks=None, **params):
        """
        Finds member shared print holdings for specified item.

        Args:
            params: dict,               parameters/limiters as specified in
                                        Metadata API documentation, see:
                                            https://developer.api.oclc.org/wc-metadata-v1-1
                                        example:
                                        {
                                            "oclcNumber": 12345,
                                            "heldInState": "NY",
                                            "limit": 50
                                        }
        """
        url = self._url_member_shared_print_holdings()
        header = {"Accept": "application/json"}

        # send request
        try:
            response = self.get(url, headers=header, params=params, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def get_brief_bib(self, oclcNumber=None, hooks=None):
        """
        Retrieve specific brief bibliographic resource.

        Args:
            oclcNumber: int or str,    OCLC bibliographic record number; can be
                                        an integer, or string that can include
                                        OCLC # prefix
            hooks: dict,                Requests library hook system that can be
                                        used for singnal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            response: requests.Response object
        """

        oclcNumber = verify_oclc_number(oclcNumber)
        header = {"Accept": "application/json"}
        url = self._url_brief_bib_oclc_number(oclcNumber)

        # send request
        try:
            response = self.get(url, headers=header, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def search_brief_bibs(
        self,
        q,
        hooks=None,
        **params,
    ):
        """
        Send a GET request for brief bibliographic resources.

        Args:
            q: str,                     query in the form of a keyword search or
                                        fielded search;
                                        examples:
                                            ti:Zendegi
                                            ti:"Czarne oceany"
                                            bn:9781680502404
                                            kw:python databases
                                            ti:Zendegi AND au:greg egan
                                            (au:Okken OR au:Myers) AND su:python

            hooks: dict,                Requests library hook system that can be
                                        used for singnal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
            params: dict,               other parameters/limiters as specified in
                                        Metadata API documentation, see:
                                            https://developer.api.oclc.org/wc-metadata-v1-1
                                        example:
                                        {
                                            "datePublished": "2010-2012",
                                            "itemType": "book",
                                            "itemSubType": "digital",
                                            "orderedBy": "mostWidelyHeld",
                                            "catalogSource": "DLC",
                                            "inLanguage": "eng",
                                            "inCatalogLanguage": "eng",
                                            "limit": 50
                                        }

            Returns:
                response: requests.Response object

        """
        url = self._url_brief_bib_search()
        header = {"Accept": "application/json"}
        payload = dict(q=q)
        payload.update(**params)

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def search_brief_bib_other_editions(self, oclcNumber=None, hooks=None, **params):
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC #.

        Args:
            oclcNumber: int or str,    OCLC bibliographic record number; can be an
                                        integer, or string with or without OCLC # prefix
            hooks: dict,                Requests library hook system that can be
                                        used for singnal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
            params: dict,               other parameters specified by Metadata API
                                        documentation, see:
                                            https://developer.api.oclc.org/wc-metadata-v1-1
                                        example:
                                            {
                                                "offset": 51,
                                                "limit": 50
                                            }
        Returns:
            response: requests.Response object
        """
        oclcNumber = verify_oclc_number(oclcNumber)
        url = self._url_brief_bib_other_editions(oclcNumber)
        header = {"Accept": "application/json"}

        # send request
        try:
            response = self.get(url, headers=header, params=params, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
