# -*- coding: utf-8 -*-

"""
This module provides MetadataSession class for requests to WorldCat Metadata API.
"""

import sys
from typing import Dict, List, Tuple, Type, Union

import requests

from ._session import WorldcatSession
from .authorize import WorldcatAccessToken
from .errors import (
    WorldcatSessionError,
    WorldcatRequestError,
    InvalidOclcNumber,
    WorldcatAuthorizationError,
)
from .utils import verify_oclc_number, verify_oclc_numbers, _parse_error_response


class MetadataSession(WorldcatSession):
    """OCLC Metadata API wrapper session. Inherits `requests.Session` methods"""

    def __init__(
        self,
        authorization: Type[WorldcatAccessToken],
        agent: str = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float]] = None,
    ):
        """
        Args:
            authorization:          WorlcatAccessToken object
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 3 seconds
        """
        WorldcatSession.__init__(self, agent=agent, timeout=timeout)

        self.authorization = authorization

        if type(self.authorization).__name__ != "WorldcatAccessToken":
            raise WorldcatSessionError(
                "Argument 'authorization' must include 'WorldcatAccessToken' obj."
            )

        self._update_authorization()

    def _update_authorization(self):
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _get_new_access_token(self):
        """
        Allows to continue sending request with new access token after
        the previous one expired
        """
        try:
            self.authorization._request_token()
            self._update_authorization()
        except WorldcatAuthorizationError as exc:
            raise WorldcatSessionError(exc)

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

    def get_brief_bib(self, oclcNumber: Union[int, str], hooks: Dict = None):
        """
        Retrieve specific brief bibliographic resource.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """

        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber:
            raise WorldcatSessionError("Invalid OCLC # was passed as an argument")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        header = {"Accept": "application/json"}
        url = self._url_brief_bib_oclc_number(oclcNumber)

        # send request
        try:
            response = self.get(url, headers=header, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def get_full_bib(
        self,
        oclcNumber: Union[int, str],
        response_format: str = None,
        hooks: Dict = None,
    ):
        """
        Send a GET request for a full bibliographic resource.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber:
            raise WorldcatSessionError("Invalid OCLC # was passed as an argument.")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_bib_oclc_number(oclcNumber)
        if not response_format:
            response_format = (
                'application/atom+xml;content="application/vnd.oclc.marc21+xml"'
            )
        header = {"Accept": response_format}

        # send request
        try:
            response = self.get(url, headers=header, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def holding_get_status(
        self,
        oclcNumber: Union[int, str],
        inst: str = None,
        instSymbol: str = None,
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Retrieves Worlcat holdings status of a record with provided OCLC number.
        The service automatically recognizes institution based on the issued access
        token.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            inst:                   registry ID of the institution whose holdings
                                    are being checked
            instSymbol:             optional; OCLC symbol of the institution whose
                                    holdings are being checked
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """
        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_bib_holdings_check()
        header = {"Accept": response_format}
        payload = {"oclcNumber": oclcNumber, "inst": inst, "instSymbol": instSymbol}

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def holding_set(
        self,
        oclcNumber: Union[int, str],
        inst: str = None,
        instSymbol: str = None,
        holdingLibraryCode: str = None,
        classificationScheme: str = None,
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Sets institution's Worldcat holding on an individual record.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            inst:                   registry ID of the institution whose holdings
                                    are being checked
            instSymbol:             optional; OCLC symbol of the institution whose
                                    holdings are being checked
            holdingLibraryCode:     four letter holding code to set the holing on
            classificationScheme:   whether or not to return group availability
                                    information
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_bib_holdings_action()
        header = {"Accept": response_format}
        payload = {
            "oclcNumber": oclcNumber,
            "inst": inst,
            "instSymbol": instSymbol,
            "holdingLibraryCode": holdingLibraryCode,
            "classificationScheme": classificationScheme,
        }

        # send request
        try:
            response = self.post(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == 201:
                # the service does not return any meaningful response
                # when holdings are succesfully set
                return response
            elif response.status_code == 409:
                # holdings already set
                # it seems resonable to simply ignore this response
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def holding_unset(
        self,
        oclcNumber: Union[int, str],
        cascade: Union[int, str] = "0",
        inst: str = None,
        instSymbol: str = None,
        holdingLibraryCode: str = None,
        classificationScheme: str = None,
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Deletes institution's Worldcat holding on an individual record.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
                                    if str the numbers must be separated by comma
            cascade:                0 or 1, default 0;
                                    0 - don't remove holdings if local holding
                                    record or local bibliographic records exists;
                                    1 - remove holding and delete local holdings
                                    record and local bibliographic record
            inst:                   registry ID of the institution whose holdings
                                    are being checked
            instSymbol:             optional; OCLC symbol of the institution whose
                                    holdings are being checked
            holdingLibraryCode:     four letter holding code to set the holing on
            classificationScheme:   whether or not to return group availability
                                    information
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_bib_holdings_action()
        header = {"Accept": response_format}
        payload = {
            "oclcNumber": oclcNumber,
            "cascade": cascade,
            "inst": inst,
            "instSymbol": instSymbol,
            "holdingLibraryCode": holdingLibraryCode,
            "classificationScheme": classificationScheme,
        }

        # send request
        try:
            response = self.delete(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                # the service does not return any meaningful response
                # when holdings are succesfully deleted
                return response
            elif response.status_code == 409:
                # holdings already set
                # it seems resonable to simply ignore this response
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def holdings_set(
        self,
        oclcNumbers: Union[str, List],
        inst: str = None,
        instSymbol: str = None,
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Set institution holdings for multiple OClC numbers

        Args:
            oclcNumbers:            list of OCLC control numbers for which holdings
                                    should be set;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
            inst:                   registry ID of the institution whose holdings
                                    are being checked
            instSymbol:             optional; OCLC symbol of the institution whose
                                    holdings are being checked
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        responses = []

        try:
            vetted_numbers = verify_oclc_numbers(oclcNumbers)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        url = self._url_bib_holdings_batch_action()
        header = {"Accept": response_format}

        # split into batches of 50 and issue request for each batch
        for batch in self._split_into_legal_volume(vetted_numbers):
            payload = {
                "oclcNumbers": batch,
                "inst": inst,
                "instSymbol": instSymbol,
            }

            # make sure access token is still valid and if not request a new one
            if self.authorization.is_expired():
                self._get_new_access_token()

            # send request
            try:
                response = self.post(url, headers=header, params=payload, hooks=hooks)

                if response.status_code == 207:
                    # the service returns multi-status response
                    responses.append(response)
                else:
                    error_msg = _parse_error_response(response)
                    raise WorldcatRequestError(error_msg)
            except WorldcatRequestError as exc:
                raise WorldcatSessionError(exc)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
            except:
                raise WorldcatSessionError(
                    f"Unexpected request error: {sys.exc_info()[0]}"
                )
        return responses

    def holdings_unset(
        self,
        oclcNumbers: Union[str, List],
        cascade: Union[int, str] = "0",
        inst: str = None,
        instSymbol: str = None,
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Set institution holdings for multiple OClC numbers

        Args:
            oclcNumbers:            list of OCLC control numbers for which holdings
                                    should be set;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
            cascade:                0 or 1, default 0;
                                    0 - don't remove holdings if local holding
                                    record or local bibliographic records exists;
                                    1 - remove holding and delete local holdings
                                    record and local bibliographic record
            inst:                   registry ID of the institution whose holdings
                                    are being checked
            instSymbol:             optional; OCLC symbol of the institution whose
                                    holdings are being checked
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        responses = []

        try:
            vetted_numbers = verify_oclc_numbers(oclcNumbers)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        url = self._url_bib_holdings_batch_action()
        header = {"Accept": response_format}

        # split into batches of 50 and issue request for each batch
        for batch in self._split_into_legal_volume(vetted_numbers):
            payload = {
                "oclcNumbers": batch,
                "cascade": cascade,
                "inst": inst,
                "instSymbol": instSymbol,
            }

            # make sure access token is still valid and if not request a new one
            if self.authorization.is_expired():
                self._get_new_access_token()

            # send request
            try:
                response = self.delete(url, headers=header, params=payload, hooks=hooks)

                if response.status_code == 207:
                    # the service returns multi-status response
                    responses.append(response)
                else:
                    error_msg = _parse_error_response(response)
                    raise WorldcatRequestError(error_msg)
            except WorldcatRequestError as exc:
                raise WorldcatSessionError(exc)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
            except:
                raise WorldcatSessionError(
                    f"Unexpected request error: {sys.exc_info()[0]}"
                )
        return responses

    def search_brief_bib_other_editions(
        self,
        oclcNumber: Union[int, str],
        offset: int = None,
        limit: int = None,
        hooks: Dict = None,
    ):
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC #.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        try:
            oclcNumber = verify_oclc_number(oclcNumber)
        except InvalidOclcNumber:
            raise WorldcatSessionError("Invalid OCLC # was passed as an argument")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_brief_bib_other_editions(oclcNumber)
        header = {"Accept": "application/json"}
        payload = {"offset": offset, "limit": limit}

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def search_brief_bibs(
        self,
        q: str,
        deweyNumber: str = None,
        datePublished: str = None,
        heldBy: str = None,
        heldByGroup: str = None,
        inLanguage: str = None,
        inCatalogLanguage: str = "eng",
        materialType: str = None,
        catalogSource: str = None,
        itemType: str = None,
        itemSubType: str = None,
        retentionCommitments: bool = None,
        spProgram: str = None,
        facets: str = None,
        groupRelatedEditions: str = None,
        orderBy: str = "mostWidelyHeld",
        offset: int = None,
        limit: int = None,
        hooks: Dict = None,
    ):
        """
        Send a GET request for brief bibliographic resources.

        Args:
            q:                      query in the form of a keyword search or
                                    fielded search;
                                    examples:
                                        ti:Zendegi
                                        ti:"Czarne oceany"
                                        bn:9781680502404
                                        kw:python databases
                                        ti:Zendegi AND au:greg egan
                                        (au:Okken OR au:Myers) AND su:python
            deweyNumber:            limits the response to the
                                    specified dewey classification number(s);
                                    for multiple values repeat the parameter,
                                    example:
                                        '794,180'
            datePublished:          restricts the response to one or
                                    more dates, or to a range,
                                    examples:
                                        '2000'
                                        '2000-2005'
                                        '2000,2005'
            heldBy:                 institution symbol; restricts to records
                                    held by indicated institution
            heldByGroup:            restricts to holdings held by group symbol
            inLanguage:             restrics the response to the single
                                    specified language, example: 'fre'
            inCataloglanguage:      restrics the response to specified
                                    cataloging language, example: 'eng';
                                    default 'eng'
            materialType:           restricts responses to specified material type,
                                    example: 'bks', 'vis'
            catalogSource:          restrict to responses to single OCLC symbol as
                                    the cataloging source, example: 'DLC'
            itemType:               restricts reponses to single specified OCLC
                                    top-level facet type, example: 'book'
            itemSubType:            restricts responses to single specified OCLC
                                    sub facet type, example: 'digital'
            retentionCommitments:   restricts responses to bibliographic records
                                    with retention commitment; True or False
            spProgram:              restricts responses to bibliographic records
                                    associated with particular shared print
                                    program
            facets:                 list of facets to restrict responses
            groupRelatedEditions:   whether or not use FRBR grouping,
                                    options: 'Y' (yes) or 'N' (no);
                                    server's default 'N'
            orderBy:                results sort key;
                                    options:
                                        'recency'
                                        'bestMatch'
                                        'creator'
                                        'publicationDateAsc'
                                        'publicationDateDesc'
                                        'mostWidelyHeld'
                                        'title'
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object

        """
        if not q:
            raise WorldcatSessionError("Argument 'q' is requried to construct query.")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_brief_bib_search()
        header = {"Accept": "application/json"}
        payload = {
            "q": q,
            "deweyNumber": deweyNumber,
            "datePublished": datePublished,
            "heldBy": heldBy,
            "heldByGroup": heldByGroup,
            "inLanguage": inLanguage,
            "inCatalogLanguage": inCatalogLanguage,
            "materialType": materialType,
            "catalogSource": catalogSource,
            "itemType": itemType,
            "itemSubType": itemSubType,
            "retentionCommitments": retentionCommitments,
            "spProgram": spProgram,
            "facets": facets,
            "groupRelatedEditions": groupRelatedEditions,
            "orderBy": orderBy,
            "offset": offset,
            "limit": limit,
        }

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatRequestError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def search_current_control_numbers(
        self,
        oclcNumbers: Union[int, str],
        response_format: str = "application/atom+json",
        hooks: Dict = None,
    ):
        """
        Retrieve current OCLC control numbers

        Args:
            oclcNumbers:            list of OCLC control numbers to be checked;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        try:
            vetted_numbers = verify_oclc_numbers(oclcNumbers)
        except InvalidOclcNumber as exc:
            raise WorldcatSessionError(exc)

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        header = {"Accept": response_format}
        url = self._url_bib_check_oclc_numbers()
        payload = {"oclcNumbers": ",".join(vetted_numbers)}

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == 207:  # multi-status response
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def search_general_holdings(
        self,
        oclcNumber: Union[int, str] = None,
        isbn: str = None,
        issn: str = None,
        holdingsAllEditions: bool = None,
        heldInCountry: str = None,
        heldByGroup: str = None,
        heldBy: str = None,
        lat: float = None,
        lon: float = None,
        distance: int = None,
        unit: str = None,
        offset: int = None,
        limit: int = None,
        hooks: Dict = None,
    ):
        """
        Given a known item gets summary of holdings.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            isbn:                   ISBN without any dashes,
                                    example: '978149191646x'
            issn:                   ISSN (hyphenated, example: '0099-1234')
            holdingsAllEditions:    get holdings for all editions;
                                    options: True or False
            heldInCountry:          restricts to holdings held by institutions
                                    in requested country
            heldByGroup:            limits to holdings held by indicated by
                                    symbol group
            heldBy:                 limits to holdings of single institution,
                                    use institution OCLC symbol
            lat:                    limit to latitude, example: 37.502508
            lon:                    limit to longitute, example: -122.22702
            distance:               distance from latitude and longitude
            unit:                   unit of distance param; options:
                                    'M' (miles) or 'K' (kilometers)
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
        Returns:
            `requests.Response` object
        """
        if not any([oclcNumber, isbn, issn]):
            raise WorldcatSessionError(
                "Missing required argument. "
                "One of the following args are required: oclcNumber, issn, isbn"
            )
        if oclcNumber is not None:
            try:
                oclcNumber = verify_oclc_number(oclcNumber)
            except InvalidOclcNumber:
                raise WorldcatSessionError("Invalid OCLC # was passed as an argument")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_member_general_holdings()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "isbn": isbn,
            "issn": issn,
            "holdingsAllEditions": holdingsAllEditions,
            "heldInCountry": heldInCountry,
            "heldByGroup": heldByGroup,
            "heldBy": heldBy,
            "lat": lat,
            "lon": lon,
            "distance": distance,
            "unit": unit,
            "offset": offset,
            "limit": limit,
        }

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Connection error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")

    def search_shared_print_holdings(
        self,
        oclcNumber: Union[int, str] = None,
        isbn: str = None,
        issn: str = None,
        heldByGroup: str = None,
        heldInState: str = None,
        offset: int = None,
        limit: int = None,
        hooks: Dict = None,
    ):
        """
        Finds member shared print holdings for specified item.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            isbn:                   ISBN without any dashes,
                                    example: '978149191646x'
            issn:                   ISSN (hyphenated, example: '0099-1234')
            heldByGroup:            restricts to holdings held by group symbol
            heldInState:            restricts to holings held by institutions
                                    in requested state, example: "NY"
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
            ""
        Returns:
            `requests.Response` object
        """
        if not any([oclcNumber, isbn, issn]):
            raise WorldcatSessionError(
                "Missing required argument. "
                "One of the following args are required: oclcNumber, issn, isbn"
            )

        if oclcNumber is not None:
            try:
                oclcNumber = verify_oclc_number(oclcNumber)
            except InvalidOclcNumber:
                raise WorldcatSessionError("Invalid OCLC # was passed as an argument")

        # make sure access token is still valid and if not request a new one
        if self.authorization.is_expired():
            self._get_new_access_token()

        url = self._url_member_shared_print_holdings()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "isbn": isbn,
            "issn": issn,
            "heldByGroup": heldByGroup,
            "heldInState": heldInState,
            "offset": offset,
            "limit": limit,
        }

        # send request
        try:
            response = self.get(url, headers=header, params=payload, hooks=hooks)
            if response.status_code == requests.codes.ok:
                return response
            else:
                error_msg = _parse_error_response(response)
                raise WorldcatRequestError(error_msg)
        except WorldcatRequestError as exc:
            raise WorldcatSessionError(exc)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatSessionError(f"Request error: {sys.exc_info()[0]}")
        except:
            raise WorldcatSessionError(f"Unexpected request error: {sys.exc_info()[0]}")
