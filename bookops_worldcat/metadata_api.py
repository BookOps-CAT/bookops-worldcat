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

    def _url_brief_bib_oclc_number(self, oclc_number):
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclc_number}"

    def _url_brief_bib_other_editions(self, oclc_number):
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclc_number}/other-editions"

    def _url_lhr_control_number(self, control_number):
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings/{control_number}"

    def _url_lhr_search(self):
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings"

    def _url_lhr_shared_print(self):
        base_url = self._url_search_base()
        return f"{base_url}/retained-holdings"

    def _url_bib_oclc_number(self, oclc_number):
        base_url = self._url_base()
        return f"{base_url}/bib/data/{oclc_number}"

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

    def get_brief_bib(self, oclc_number=None, hooks=None):
        """
        Retrieve specific brief bibliographic resource.

        Args:
            oclc_number: int or str,    OCLC bibliographic record number; can be an integer,
                                        or string that can include OCLC # prefix
            hooks: dict,                Requests library hook system that can be
                                        used for singnal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            response: requests.Response object
        """

        # oclc_number = verify_oclc_number(oclc_number)
        header = {"Accept": "application/json"}
        url = self._url_brief_bib_oclc_number(oclc_number)

        # send request
        try:
            response = self.get(url, headers=header, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def get_brief_bib_other_editions(
        self, oclc_number=None, offset=None, limit=None, hooks=None
    ):
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC #.

        Args:
            oclc_number: int or str,    OCLC bibliographic record number; can be an
                                        integer, or string with or without OCLC # prefix
            offset: int,                start position of the bib records to return
                                        (1 based)
            limit: int,                 maximum number of records to return; maximum 50
            hooks: dict,                Requests library hook system that can be
                                        used for singnal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            response: requests.Response object
        """
        oclc_number = verify_oclc_number(oclc_number)
        url = self._url_brief_bib_other_editions(oclc_number)
        header = {"Accept": "application/json"}
        payload = {"offset": offset, "limit": limit}

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            return response
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
