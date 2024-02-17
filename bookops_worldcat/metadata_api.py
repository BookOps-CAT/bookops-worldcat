# -*- coding: utf-8 -*-

"""
This module provides MetadataSession class for requests to WorldCat Metadata API.
"""

from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union

from requests import Request, Response

from ._session import WorldcatSession
from .authorize import WorldcatAccessToken
from .query import Query
from .utils import verify_oclc_number, verify_oclc_numbers


class MetadataSession(WorldcatSession):
    """OCLC Metadata API wrapper session. Inherits `requests.Session` methods"""

    def __init__(
        self,
        authorization: WorldcatAccessToken,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = None,
    ) -> None:
        """
        Args:
            authorization:          WorlcatAccessToken object
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 5 seconds
        """
        super().__init__(authorization, agent=agent, timeout=timeout)

    def _split_into_legal_volume(
        self, oclc_numbers: List[str] = [], n: int = 50
    ) -> Iterator[str]:
        """
        OCLC requries that no more than 50 numbers are passed for batch processing

        Args:
            oclc_numbers:           list of oclc numbers
            n:                      batch size, default (max) 50

        Yields:
            n-sized batch
        """

        for i in range(0, len(oclc_numbers), n):
            yield ",".join(oclc_numbers[i : i + n])  # noqa: E203

    def _url_base(self) -> str:
        return "https://worldcat.org"

    def _url_search_base(self) -> str:
        return "https://americas.metadata.api.oclc.org/worldcat/search/v1"

    def _url_member_shared_print_holdings(self) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/bibs-retained-holdings"

    def _url_member_general_holdings(self) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/bibs-summary-holdings"

    def _url_brief_bib_search(self) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs"

    def _url_brief_bib_oclc_number(self, oclcNumber: str) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclcNumber}"

    def _url_brief_bib_other_editions(self, oclcNumber: str) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/brief-bibs/{oclcNumber}/other-editions"

    def _url_lhr_control_number(self, controlNumber: str) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings/{controlNumber}"

    def _url_lhr_search(self) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/my-holdings"

    def _url_lhr_shared_print(self) -> str:
        base_url = self._url_search_base()
        return f"{base_url}/retained-holdings"

    def _url_bib_oclc_number(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/bib/data/{oclcNumber}"

    def _url_bib_check_oclc_numbers(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/bib/checkcontrolnumbers"

    def _url_bib_holding_libraries(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/bib/holdinglibraries"

    def _url_bib_holdings_action(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/ih/data"

    def _url_bib_holdings_check(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/ih/checkholdings"

    def _url_bib_holdings_batch_action(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/ih/datalist"

    def _url_bib_holdings_multi_institution_batch_action(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/ih/institutionlist"

    def get_brief_bib(
        self, oclcNumber: Union[int, str], hooks: Optional[Dict[str, Callable]] = None
    ) -> Optional[Response]:
        """
        Retrieve specific brief bibliographic resource.
        Uses /brief-bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        header = {"Accept": "application/json"}
        url = self._url_brief_bib_oclc_number(oclcNumber)

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_full_bib(
        self,
        oclcNumber: Union[int, str],
        response_format: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Send a GET request for a full bibliographic resource.
        Uses /bib/data/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            response_format:        format of returned record
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_bib_oclc_number(oclcNumber)
        if not response_format:
            response_format = (
                'application/atom+xml;content="application/vnd.oclc.marc21+xml"'
            )
        header = {"Accept": response_format}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holding_get_status(
        self,
        oclcNumber: Union[int, str],
        inst: Optional[str] = None,
        instSymbol: Optional[str] = None,
        response_format: Optional[str] = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieves Worlcat holdings status of a record with provided OCLC number.
        The service automatically recognizes institution based on the issued access
        token.
        Uses /ih/checkholdings endpoint.

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
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_bib_holdings_check()
        header = {"Accept": response_format}
        payload = {"oclcNumber": oclcNumber, "inst": inst, "instSymbol": instSymbol}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holding_set(
        self,
        oclcNumber: Union[int, str],
        inst: Optional[str] = None,
        instSymbol: Optional[str] = None,
        holdingLibraryCode: Optional[str] = None,
        classificationScheme: Optional[str] = None,
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Sets institution's Worldcat holding on an individual record.
        Uses /ih/data endpoint.

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
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_bib_holdings_action()
        header = {"Accept": response_format}
        payload = {
            "oclcNumber": oclcNumber,
            "inst": inst,
            "instSymbol": instSymbol,
            "holdingLibraryCode": holdingLibraryCode,
            "classificationScheme": classificationScheme,
        }

        # prep request
        req = Request("POST", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holding_unset(
        self,
        oclcNumber: Union[int, str],
        cascade: Union[int, str] = "0",
        inst: Optional[str] = None,
        instSymbol: Optional[str] = None,
        holdingLibraryCode: Optional[str] = None,
        classificationScheme: Optional[str] = None,
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Deletes institution's Worldcat holding on an individual record.
        Uses /ih/data endpoint.

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
        oclcNumber = verify_oclc_number(oclcNumber)

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

        # prep request
        req = Request("DELETE", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holdings_set(
        self,
        oclcNumbers: Union[str, List],
        inst: Optional[str] = None,
        instSymbol: Optional[str] = None,
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> List[Optional[Response]]:
        """
        Set institution holdings for multiple OCLC numbers
        Uses /ih/datalist endpoint.

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
            list of `requests.Response` objects
        """
        responses = []
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        url = self._url_bib_holdings_batch_action()
        header = {"Accept": response_format}

        # split into batches of 50 and issue request for each batch
        for batch in self._split_into_legal_volume(vetted_numbers):
            payload = {
                "oclcNumbers": batch,
                "inst": inst,
                "instSymbol": instSymbol,
            }

            # prep request
            req = Request("POST", url, params=payload, headers=header, hooks=hooks)
            prepared_request = self.prepare_request(req)

            # send request
            query = Query(self, prepared_request, timeout=self.timeout)

            responses.append(query.response)

        return responses

    def holdings_unset(
        self,
        oclcNumbers: Union[str, List],
        cascade: str = "0",
        inst: Optional[str] = None,
        instSymbol: Optional[str] = None,
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> List[Optional[Response]]:
        """
        Set institution holdings for multiple OCLC numbers
        Uses /ih/datalist endpoint.

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
            list of `requests.Response` objects
        """
        responses = []
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

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

            # prep request
            req = Request("DELETE", url, params=payload, headers=header, hooks=hooks)
            prepared_request = self.prepare_request(req)

            # send request
            query = Query(self, prepared_request, timeout=self.timeout)

            responses.append(query.response)

        return responses

    def holdings_set_multi_institutions(
        self,
        oclcNumber: Union[int, str],
        instSymbols: str,
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Batch sets intitution holdings for multiple intitutions

        Uses /ih/institutionlist endpoint

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            instSymbols:            a comma-separated list of OCLC symbols of the
                                    institution whose holdings are being set
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_bib_holdings_multi_institution_batch_action()
        header = {"Accept": response_format}
        payload = {
            "oclcNumber": oclcNumber,
            "instSymbols": instSymbols,
        }

        # prep request
        req = Request("POST", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holdings_unset_multi_institutions(
        self,
        oclcNumber: Union[int, str],
        instSymbols: str,
        cascade: str = "0",
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Batch unsets intitution holdings for multiple intitutions

        Uses /ih/institutionlist endpoint

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            instSymbols:            a comma-separated list of OCLC symbols of the
                                    institution whose holdings are being set
            cascade:                0 or 1, default 0;
                                    0 - don't remove holdings if local holding
                                    record or local bibliographic records exists;
                                    1 - remove holding and delete local holdings
                                    record and local bibliographic record
            response_format:        'application/atom+json' (default) or
                                    'application/atom+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_bib_holdings_multi_institution_batch_action()
        header = {"Accept": response_format}
        payload = {
            "oclcNumber": oclcNumber,
            "instSymbols": instSymbols,
            "cascade": cascade,
        }

        # prep request
        req = Request("DELETE", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_brief_bib_other_editions(
        self,
        oclcNumber: Union[int, str],
        deweyNumber: Optional[str] = None,
        datePublished: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[str] = None,
        heldByInstitutionID: Optional[Union[str, int]] = None,
        inLanguage: Optional[str] = None,
        inCatalogLanguage: Optional[str] = None,
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[str] = None,
        itemSubType: Optional[str] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[str] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[str] = None,
        groupVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        orderBy: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC #.
        Uses /brief-bibs/{oclcNumber}/other-editions endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
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
            heldByGroup:            restricts to holdings held by group symbol
            heldBySymbol:           restricts to holdings with specified intitution
                                    symbol
            heldByInstitutionID:    restrict to specified institution regisgtryId
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
                                    with retention commitment; True or False,
                                    default False
            spProgram:              restricts responses to bibliographic records
                                    associated with particular shared print
                                    program
            genre:                  genre to limit results to
            topic:                  topic to limit results to
            subtopic:               subtopic to limit results to
            audience:               audience to limit results to,
                                    example:
                                        juv,
                                        nonJuv
            content:                content to limit resutls to,
                                    example:
                                        fic,
                                        nonFic,
                                        fic,bio
            openAccess:             filter to only open access content, False or True
            peerReviewed:           filter to only peer reviewed content, False or True
            facets:                 list of facets to restrict responses
            groupVariantRecords:    whether or not to group variant records.
                                    options: False, True (default False)
            preferredLanguage:      language of metadata description,
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
            orderBy:                sort of restuls;
                                    available values:
                                        +date, -date, +language, -language;
                                    default value: -date
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_brief_bib_other_editions(oclcNumber)
        header = {"Accept": "application/json"}
        payload = {
            "deweyNumber": deweyNumber,
            "datePublished": datePublished,
            "heldByGroup": heldByGroup,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "inLanguage": inLanguage,
            "inCatalogLanguage": inCatalogLanguage,
            "catalogSource": catalogSource,
            "itemType": itemType,
            "itemSubType": itemSubType,
            "retentionCommitments": retentionCommitments,
            "spProgram": spProgram,
            "genre": genre,
            "topic": topic,
            "subtopic": subtopic,
            "audience": audience,
            "content": content,
            "openAccess": openAccess,
            "peerReviewed": peerReviewed,
            "facets": facets,
            "groupVariantRecords": groupVariantRecords,
            "preferredLanguage": preferredLanguage,
            "offset": offset,
            "limit": limit,
            "orderBy": orderBy,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_brief_bibs(
        self,
        q: str,
        deweyNumber: Optional[str] = None,
        datePublished: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        inLanguage: Optional[str] = None,
        inCatalogLanguage: Optional[str] = "eng",
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[str] = None,
        itemSubType: Optional[str] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        facets: Optional[str] = None,
        groupRelatedEditions: Optional[bool] = None,
        groupVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        orderBy: Optional[str] = "mostWidelyHeld",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Send a GET request for brief bibliographic resources.
        Uses /brief-bibs endpoint.

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
                                    options: False, True (default is False)
            groupVariantRecords:    whether or not to group variant records.
                                    options: False, True (default False)
            preferredLanguage:      language of metadata description,
                                    default value "en" (English)
            orderBy:                results sort key;
                                    options:
                                        'recency'
                                        'bestMatch'
                                        'creator'
                                        'library'
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
            raise TypeError("Argument 'q' is requried to construct query.")

        url = self._url_brief_bib_search()
        header = {"Accept": "application/json"}
        payload = {
            "q": q,
            "deweyNumber": deweyNumber,
            "datePublished": datePublished,
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
            "groupVariantRecords": groupVariantRecords,
            "preferredLanguage": preferredLanguage,
            "orderBy": orderBy,
            "offset": offset,
            "limit": limit,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_current_control_numbers(
        self,
        oclcNumbers: Union[str, List[Union[str, int]]],
        response_format: str = "application/atom+json",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve current OCLC control numbers
        Uses /bib/checkcontrolnumbers endpoint.

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

        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        header = {"Accept": response_format}
        url = self._url_bib_check_oclc_numbers()
        payload = {"oclcNumbers": ",".join(vetted_numbers)}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_general_holdings(
        self,
        oclcNumber: Union[int, str, None] = None,
        isbn: Optional[str] = None,
        issn: Optional[str] = None,
        holdingsAllEditions: Optional[bool] = None,
        holdingsAllVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        heldInCountry: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        distance: Optional[int] = None,
        unit: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a known item gets summary of holdings.
        Uses /bibs-summary-holdings endpoint.

        Args:
            oclcNumber:                 OCLC bibliographic record number; can be
                                        an integer, or string that can include
                                        OCLC # prefix
            isbn:                       ISBN without any dashes,
                                        example: '978149191646x'
            issn:                       ISSN (hyphenated, example: '0099-1234')
            holdingsAllEditions:        get holdings for all editions;
                                        options: True or False
            holdingsAllVariantRecords:  get holdings for specific edition across variant
                                        records; options: False, True
            preferredLanguage:          language of metadata description;
                                        default 'en' (English)
            heldInCountry:              restricts to holdings held by institutions
                                        in requested country
            heldByGroup:                limits to holdings held by indicated by
                                        symbol group
            lat:                        limit to latitude, example: 37.502508
            lon:                        limit to longitute, example: -122.22702
            distance:                   distance from latitude and longitude
            unit:                       unit of distance param; options:
                                        'M' (miles) or 'K' (kilometers)
            offset:                     start position of bibliographic records to
                                        return; default 1
            limit:                      maximum nuber of records to return;
                                        maximum 50, default 10
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if not any([oclcNumber, isbn, issn]):
            raise TypeError(
                "Missing required argument. "
                "One of the following args are required: oclcNumber, issn, isbn"
            )
        if oclcNumber is not None:
            oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_member_general_holdings()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "isbn": isbn,
            "issn": issn,
            "holdingsAllEditions": holdingsAllEditions,
            "holdingsAllVariantRecords": holdingsAllVariantRecords,
            "preferredLanguage": preferredLanguage,
            "heldInCountry": heldInCountry,
            "heldByGroup": heldByGroup,
            "lat": lat,
            "lon": lon,
            "distance": distance,
            "unit": unit,
            "offset": offset,
            "limit": limit,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_shared_print_holdings(
        self,
        oclcNumber: Union[int, str, None] = None,
        isbn: Optional[str] = None,
        issn: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        heldInState: Optional[str] = None,
        itemType: Optional[str] = None,
        itemSubType: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Finds member shared print holdings for specified item.
        Uses /bibs-retained-holdings endpoint.

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
            itemType:               restricts results to specified item type (example
                                    'book' or 'vis')
            itemSubType:            restricts results to specified item sub type
                                    examples: 'book-digital' or 'audiobook-cd'
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
            ""
        Returns:
            `requests.Response` object
        """
        if not any([oclcNumber, isbn, issn]):
            raise TypeError(
                "Missing required argument. "
                "One of the following args are required: oclcNumber, issn, isbn"
            )

        if oclcNumber is not None:
            oclcNumber = verify_oclc_number(oclcNumber)

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

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response
