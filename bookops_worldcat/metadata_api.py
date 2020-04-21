# -*- coding: utf-8 -*-

import requests

from ._session import WorldcatSession


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

        self.base_url = "https://worldcat.org/bib"
        self.token = credentials
        self.headers.update({"Authorization": f"Bearer {self.token.token_str}"})

    def _get_record_url(self, oclc_number):
        return f"{self.base_url}/data/{oclc_number}"

    def get_record(self, oclc_number=None, hooks=None):
        """
        Sends a request for a record with OCLC number provided as an argument.

        Args:
            oclc_number: str,       OCLC bibliographic record number; do not include
                                    any prefix, only digits.
            hooks: dict,            requests library hook system that can be used for
                                    singal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            response: requests.Response object
        """
        if oclc_number is None:
            raise TypeError("Argument oclc_number cannot be None.")
        # alternatively remove oclc prefix?
        if "o" in oclc_number:
            raise ValueError("Argument oclc_number must include only digits.")

        # request header
        header = {
            "Accept": 'application/atom+xml;content="application/vnd.oclc.marc21+xml"'
        }

        url = self._get_record_url(oclc_number)

        # send request
        try:
            response = self.get(url, headers=header, hooks=hooks, timeout=self.timeout)
            return response

        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
