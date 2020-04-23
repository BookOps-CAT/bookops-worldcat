# -*- coding: utf-8 -*-

import requests

from ._session import WorldcatSession
from .constant import HOLDINGS_RESPONSE_FORMATS


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

        self.base_url = "https://worldcat.org"
        self.token = credentials
        self.headers.update({"Authorization": f"Bearer {self.token.token_str}"})

    def _get_record_url(self, oclc_number):
        return f"{self.base_url}/bib/data/{oclc_number}"

    def _holdings_set_and_unset_url(self):
        return f"{self.base_url}/ih/data"

    def _holdings_status_url(self):
        return f"{self.base_url}/ih/checkholdings"

    def _split_into_legal_volume(self, oclc_numbers=[]):
        """
        OCLC requries that no more than 50 numbers are passed for batch processing
        """
        incomplete = True
        batches = []
        start = 0
        end = 50
        while incomplete:
            batch = oclc_numbers[start:end]
            if not batch:
                incomplete = False
            elif len(batch) < 50:
                batches.append(",".join([str(x) for x in batch]))
                incomplete = False
            else:
                batches.append(",".join([str(x) for x in batch]))
                start += 50
                end += 50

        return batches

    def _verify_oclc_number(self, oclc_number):
        """Verifies a valid looking OCLC number is passed to a request"""
        if oclc_number is None:
            raise TypeError("Missing argument oclc_number.")
        elif type(oclc_number) is not str:
            raise TypeError("Argument oclc_number must be a string.")
        # alternatively remove oclc prefix?
        elif "o" in oclc_number:
            raise ValueError("Argument oclc_number (string) must include only digits.")
        else:
            return oclc_number

    def _verify_holdings_response_argument(self, response_format):
        """Verifies a valid holdings_response_format is used in a request"""
        if response_format is None:
            response_format = "json"
        if response_format not in HOLDINGS_RESPONSE_FORMATS.keys():
            raise ValueError("Invalid argument response_format.")
        else:
            return HOLDINGS_RESPONSE_FORMATS[response_format]

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

        oclc_number = self._verify_oclc_number(oclc_number)

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

    def holdings_get_status(
        self, oclc_number, response_format="json", hooks=None,
    ):
        """
        Retrieves holdings status of record with provided OCLC number. The service
        automatically recognizes institution based on the access token

        Args:
            oclc_number: str,               OCLC record number without any prefix
            response_format: str,           "json" or "xml"; default json;

        Returns:
            request.Response object
        """

        oclc_number = self._verify_oclc_number(oclc_number)

        # set header with a valid respone format and determine payload
        auth_response_format = self._verify_holdings_response_argument(response_format)
        header = {"Accept": auth_response_format}
        payload = {"oclcNumber": oclc_number}

        url = self._holdings_status_url()

        # send request
        try:
            response = self.get(
                url, headers=header, params=payload, hooks=hooks, timeout=self.timeout
            )
            return response

        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def holdings_set(self, oclc_number, response_format="json", hooks=None):
        """
        Sets institution's holdings on an individual record.

        Args:
            oclc_number: str,               OCLC record number without prefix
            response_format: str,           "json" or "xml"; default json

        Returns:
            request.Response object
        """

        oclc_number = self._verify_oclc_number(oclc_number)

        # set header and payload
        auth_response_format = self._verify_holdings_response_argument(response_format)
        header = {"Accept": auth_response_format}
        payload = {"oclcNumber": oclc_number}

        url = self._holdings_set_and_unset_url()

        # send request
        try:
            response = self.post(
                url, headers=header, params=payload, hooks=hooks, timeout=self.timeout
            )
            return response

        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def holdings_unset(self, oclc_number, response_format="json", hooks=None):
        """Deletes intitution's holdings on an individual record.

        Args:
            oclc_number: str,               OCLC record number without prefix
            response_format: str,           "json" or "xml"; default json

        Returns:
            request.Response object
        """

        oclc_number = self._verify_oclc_number(oclc_number)

        # set header and payload
        auth_response_format = self._verify_holdings_response_argument(response_format)
        header = {"Accept": auth_response_format}
        payload = {"oclcNumber": oclc_number}

        url = self._holdings_set_and_unset_url()

        # send request
        try:
            response = self.delete(
                url, headers=header, params=payload, hooks=hooks, timeout=self.timeout
            )
            return response

        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
