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

    def URL_BASE(self) -> str:
        return "https://metadata.api.oclc.org/worldcat"

    def _url_manage_bib_validate(self, validationLevel: str) -> str:
        return f"{self.URL_BASE()}/manage/bibs/validate/{validationLevel}"

    def _url_manage_bib_current_oclc_number(self) -> str:
        return f"{self.URL_BASE()}/manage/bibs/current"

    def _url_manage_bib_create(self) -> str:
        return f"{self.URL_BASE()}/manage/bibs"

    def _url_manage_bib(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/manage/bibs/{oclcNumber}"

    def _url_manage_bib_match(self) -> str:
        return f"{self.URL_BASE()}/manage/bibs/match"

    def _url_manage_ih_current(self) -> str:
        return f"{self.URL_BASE()}/manage/institution/holdings/current"

    def _url_manage_ih_set(self) -> str:
        return f"{self.URL_BASE()}/manage/institution/holdings/set"

    def _url_manage_ih_unset(self) -> str:
        return f"{self.URL_BASE()}/manage/institution/holdings/unset"

    def _url_manage_ih_oclc_number_set(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/manage/institution/holdings/{oclcNumber}/set"

    def _url_manage_ih_oclc_number_unset(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/manage/institution/holdings/{oclcNumber}/unset"

    def _url_manage_ih_codes(self) -> str:
        return f"{self.URL_BASE()}/manage/institution/holding-codes"

    def _url_manage_lbd_create(self) -> str:
        return f"{self.URL_BASE()}/manage/lbds"

    def _url_manage_lbd(self, controlNumber: str) -> str:
        return f"{self.URL_BASE()}/manage/lbds/{controlNumber}"

    def _url_manage_lhr_create(self) -> str:
        return f"{self.URL_BASE()}/manage/lhrs"

    def _url_manage_lhr(self, controlNumber: str) -> str:
        return f"{self.URL_BASE()}/manage/lhrs/{controlNumber}"

    def _url_search_shared_print_holdings(self) -> str:
        return f"{self.URL_BASE()}/search/bibs-retained-holdings"

    def _url_search_general_holdings(self) -> str:
        return f"{self.URL_BASE()}/search/bibs-summary-holdings"

    def _url_search_general_holdings_summary(self) -> str:
        return f"{self.URL_BASE()}/search/summary-holdings"

    def _url_search_brief_bibs(self) -> str:
        return f"{self.URL_BASE()}/search/brief-bibs"

    def _url_search_brief_bibs_oclc_number(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/search/brief-bibs/{oclcNumber}"

    def _url_search_brief_bibs_other_editions(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/search/brief-bibs/{oclcNumber}/other-editions"

    def _url_search_classification_bibs(self, oclcNumber: str) -> str:
        return f"{self.URL_BASE()}/search/classification-bibs/{oclcNumber}"

    def _url_search_lhr_shared_print(self) -> str:
        return f"{self.URL_BASE()}/search/retained-holdings"

    def _url_search_lhr_control_number(self, controlNumber: str) -> str:
        return f"{self.URL_BASE()}/search/my-holdings/{controlNumber}"

    def _url_search_lhr(self) -> str:
        return f"{self.URL_BASE()}/search/my-holdings"

    def _url_browse_lhr(self) -> str:
        return f"{self.URL_BASE()}/browse/my-holdings"

    def _url_search_lbd_control_number(self, controlNumber: str) -> str:
        return f"{self.URL_BASE()}/search/my-local-bib-data/{controlNumber}"

    def _url_search_lbd(self) -> str:
        return f"{self.URL_BASE()}/search/my-local-bib-data"

    def create_bib(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Create a bib record in OCLC if it does not already exist
        Uses /manage/bibs/ endpoint.

        Args:
            record:                 MARC record to be created
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            responseFormat:         format of returned record; options:
                                    'application/marcxml+xml', 'application/marc'
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        if not record:
            raise TypeError("Argument 'record' is missing.")
        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")

        if not responseFormat:
            responseFormat = "application/marcxml+xml"

        url = self._url_manage_bib_create()
        header = {
            "Accept": responseFormat,
            "content-type": recordFormat,
        }

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_bib_classification(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number, retrieve classification recommendations for the bib record
        Uses /search/classification-bibs/{oclcNumber}/ endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_classification_bibs(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_bib_holdings(
        self,
        oclcNumber: Union[int, str],
        holdingsAllEditions: Optional[bool] = None,
        holdingsAllVariantRecords: Optional[bool] = None,
        holdingsFilterFormat: Optional[List[str]] = None,
        heldInCountry: Optional[str] = None,
        heldInState: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[List[str]] = None,
        heldByInstitutionID: Optional[List[int]] = None,
        heldByLibraryType: Optional[List[str]] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        distance: Optional[int] = None,
        unit: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number get summary of holdings
        Uses /search/summary-holdings/ endpoint.

        Args:
            oclcNumber:                 OCLC bibliographic record number; can be
                                        an integer or string with or without OCLC #
                                        prefix
            holdingsAllEditions:        get holdings for all editions;
                                        options: True, False, default is False
            holdingsAllVariantRecords:  get holdings for specific edition across
                                        all variant records; options: True, False,
                                        default is False
            holdingsFilterFormat:       get holdings for specific itemSubType,
                                        example: book-digital
            heldInCountry:              limits to holdings held by institutions
                                        in requested country
            heldInState:                limits to holdings held by institutions
                                        in requested state, example: 'US-NY'
            heldByGroup:                limits to holdings held by institutions
                                        indicated by group symbol
            heldBySymbol:               limits to holdings held by institutions
                                        indicated by institution symbol
            heldByInstitutionID:        limits to holdings held by institutions
                                        indicated by institution registryID
            heldByLibraryType:          limits to holdings held by library type,
                                        options: 'PUBLIC', 'ALL'
            lat:                        limit to latitude, example: 37.502508
            lon:                        limit to longitute, example: -122.22702
            distance:                   distance from latitude and longitude
            unit:                       unit of distance param; options:
                                        'M' (miles) or 'K' (kilometers)
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_general_holdings_summary()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "holdingsAllEditions": holdingsAllEditions,
            "holdingsAllVariantRecords": holdingsAllVariantRecords,
            "holdingsFilterFormat": holdingsFilterFormat,
            "heldInCountry": heldInCountry,
            "heldInState": heldInState,
            "heldByGroup": heldByGroup,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "heldByLibraryType": heldByLibraryType,
            "lat": lat,
            "lon": lon,
            "distance": distance,
            "unit": unit,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_brief_bib(
        self, oclcNumber: Union[int, str], hooks: Optional[Dict[str, Callable]] = None
    ) -> Optional[Response]:
        """
        Retrieve specific brief bibliographic resource.
        Uses /search/brief-bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_brief_bibs_oclc_number(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_current_oclc_number(
        self,
        oclcNumbers: Union[str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given one or more OCLC numbers, retrieve current OCLC control numbers.
        Returns null if OCLC number is invalid or does not exist.
        Uses /manage/bibs/current endpoint.

        Args:
            oclcNumbers:            string or list containing one or more OCLC numbers
                                    to be checked; numbers can be integers or strings
                                    with or without OCLC # prefix;
                                    if str, the numbers must be separated by a comma
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        url = self._url_manage_bib_current_oclc_number()
        header = {"Accept": "application/json"}
        payload = {"oclcNumbers": ",".join(vetted_numbers)}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_full_bib(
        self,
        oclcNumber: Union[int, str],
        responseFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number, retrieve the bib record
        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            responseFormat:         format of returned record; options:
                                    'application/marcxml+xml', 'application/marc'
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        if not responseFormat:
            responseFormat = "application/marcxml+xml"

        url = self._url_manage_bib(oclcNumber)
        header = {"Accept": responseFormat}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_institution_holding_codes(
        self,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve the all holding codes for the authenticated institution.
        Uses /manage/institution/holding-codes/ endpoint.

        Args:
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_manage_ih_codes()
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_institution_holdings(
        self,
        oclcNumbers: Union[str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieves Worldcat holdings status of records with provided OCLC number(s).
        The service automatically recognizes institution based on the issued access
        token.
        Uses /manage/institution/holdings/current/ endpoint.

        Args:
            oclcNumbers:            string or list containing one or more OCLC numbers
                                    to be checked; numbers can be integers or strings
                                    with or without OCLC # prefix;
                                    if str, the numbers must be separated by a comma
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        url = self._url_manage_ih_current()
        header = {"Accept": "application/json"}
        payload = {"oclcNumbers": ",".join(vetted_numbers)}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def match_bib(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a bib record in MARC21 or MARCXML identify the best match.
        Record must contain at minimum an 008 and 245. Response contains number of
        potential matches in numberOfRecords and best match in briefRecords
        Uses /manage/bibs/match endpoint.

        Args:
            record:                 MARC record to be matched
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        if not record:
            raise TypeError("Argument 'record' is missing.")
        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")

        url = self._url_manage_bib_match()
        header = {
            "Accept": "application/json",
            "content-type": recordFormat,
        }

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def replace_bib(
        self,
        oclcNumber: Union[int, str],
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number and MARC record, find record in WorldCat and replace it
        with the new bib record. If the bib record does not exist, then a new bib record
        will be created.
        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number for record to be
                                    replaced; can be an integer or string with or
                                    without OCLC # prefix
            record:                 MARC record to replace old record
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            responseFormat:         format of returned record; options:
                                    'application/marcxml+xml', 'application/marc'
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        if not record:
            raise TypeError("Argument 'record' is missing.")
        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")
        if not responseFormat:
            responseFormat = "application/marcxml+xml"

        url = self._url_manage_bib(oclcNumber)
        header = {
            "Accept": responseFormat,
            "content-type": recordFormat,
        }

        # prep request
        req = Request("PUT", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_bib_holdings(
        self,
        oclcNumber: Optional[Union[int, str]] = None,
        isbn: Optional[str] = None,
        issn: Optional[str] = None,
        holdingsAllEditions: Optional[bool] = None,
        holdingsAllVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        holdingsFilterFormat: Optional[List[str]] = None,
        heldInCountry: Optional[str] = None,
        heldInState: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[List[str]] = None,
        heldByInstitutionID: Optional[List[int]] = None,
        heldByLibraryType: Optional[List[str]] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        distance: Optional[int] = None,
        unit: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a known item, get summary of holdings and brief bib record.
        Uses /search/bibs-summary-holdings endpoint.

        Args:
            oclcNumber:                 OCLC bibliographic record number; can be
                                        an integer or string with or without OCLC #
                                        prefix
            isbn:                       ISBN without any dashes,
                                        example: '978149191646x'
            issn:                       ISSN hyphenated, example: '0099-1234'
            holdingsAllEditions:        get holdings for all editions;
                                        options: True, False, default is False
            holdingsAllVariantRecords:  get holdings for specific edition across variant
                                        records; options: True, False, default is False
            preferredLanguage:          language of metadata description;
                                        default is 'en' (English)
            holdingsFilterFormat:       get holdings for specific itemSubType,
                                        example: book-digital
            heldInCountry:              limits to holdings held by institutions
                                        in requested country
            heldInState:                limits to holdings held by institutions
                                        in requested state, example: 'US-NY'
            heldByGroup:                limits to holdings held by institutions
                                        indicated by group symbol
            heldBySymbol:               limits to holdings held by institutions
                                        indicated by institution symbol
            heldByInstitutionID:        limits to holdings held by institutions
                                        indicated by institution registryID
            heldByLibraryType:          limits to holdings held by library type,
                                        options: 'PUBLIC', 'ALL'
            lat:                        limit to latitude, example: 37.502508
            lon:                        limit to longitute, example: -122.22702
            distance:                   distance from latitude and longitude
            unit:                       unit of distance param; options:
                                        'M' (miles) or 'K' (kilometers)
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

        url = self._url_search_general_holdings()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "isbn": isbn,
            "issn": issn,
            "holdingsAllEditions": holdingsAllEditions,
            "holdingsAllVariantRecords": holdingsAllVariantRecords,
            "preferredLanguage": preferredLanguage,
            "holdingsFilterFormat": holdingsFilterFormat,
            "heldInCountry": heldInCountry,
            "heldInState": heldInState,
            "heldByGroup": heldByGroup,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "heldByLibraryType": heldByLibraryType,
            "lat": lat,
            "lon": lon,
            "distance": distance,
            "unit": unit,
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
        deweyNumber: Optional[List[str]] = None,
        datePublished: Optional[List[str]] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[List[str]] = None,
        heldByInstitutionID: Optional[List[int]] = None,
        inLanguage: Optional[List[str]] = None,
        inCatalogLanguage: Optional[str] = "eng",
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[List[str]] = None,
        itemSubType: Optional[List[str]] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[List[str]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[List[str]] = None,
        groupRelatedEditions: Optional[bool] = None,
        groupVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        showHoldingsIndicators: Optional[bool] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        distance: Optional[int] = None,
        unit: Optional[str] = None,
        orderBy: Optional[str] = "mostWidelyHeld",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Search for brief bibliographic resources.
        Uses /search/brief-bibs endpoint.

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
                                    examples:
                                        '794,180'
                                        '794'
            datePublished:          limits the response to one or more dates or ranges
                                    examples:
                                        '2000'
                                        '2000-2005'
                                        '2000,2005'
                                        '2000-2002,2003-2005'
            heldByGroup:            restricts response to holdings held by group symbol
            heldBySymbol:           restricts response to holdings held by specified
                                    institution symbol
            heldByInstitutionID:    restricts response to holdings held by specified
                                    institution registryId
            inLanguage:             restricts response to the single
                                    specified language, example: 'fre'
            inCataloglanguage:      restricts response to specified
                                    cataloging language, example: 'eng';
                                    default is 'eng'
            materialType:           restricts response to specified material type,
                                    example: 'bks', 'vis'
            catalogSource:          restricts response to single OCLC symbol as
                                    the cataloging source, example: 'DLC'
            itemType:               restricts reponses to single specified OCLC
                                    top-level facet type, example: 'book'
            itemSubType:            restricts response to single specified OCLC
                                    sub facet type, example: 'digital'
            retentionCommitments:   restricts response to bibliographic records
                                    with retention commitment; options: True, False,
                                    default is False
            spProgram:              restricts response to bibliographic records
                                    associated with particular shared print
                                    program
            genre:                  genre to limit results to (ge index)
            topic:                  topic to limit results to (s0 index)
            subtopic:               subtopic to limit results to (s1 index)
            audience:               audience to limit results to,
                                    available values: 'juv', 'nonJuv'
            content:                content to limit results to
                                    available values: 'fic', 'nonFic', 'bio'
            openAccess:             restricts response to just open access content
            peerReviewed:           restricts response to just peer reviewed content
            facets:                 list of facets requested in response
                                    available values: 'subject', 'creator',
                                    'datePublished', 'genre', 'itemType',
                                    'itemSubTypeBrief', 'itemSubType', 'language',
                                    'topic', 'subtopic', 'content', 'audience',
                                    'databases'
            groupRelatedEditions:   whether or not use FRBR grouping,
                                    options: True, False, default is False
            groupVariantRecords:    whether or not to group variant records.
                                    options: True, False, default is False
            preferredLanguage:      language of metadata description,
                                    default is 'en' (English)
            showHoldingsIndicators: whether or not to show holdings indicators in
                                    response. options: True, False, default is False
            lat:                    limit to latitude, example: 37.502508
            lon:                    limit to longitute, example: -122.22702
            distance:               distance from latitude and longitude
            unit:                   unit of distance param; options:
                                    'M' (miles) or 'K' (kilometers)
            orderBy:                results sort key;
                                    options:
                                        'library'
                                        'recency'
                                        'bestMatch'
                                        'creator'
                                        'publicationDateAsc'
                                        'publicationDateDesc'
                                        'mostWidelyHeld'
                                        'title'
                                    default is bestMatch
            offset:                 start position of bibliographic records to
                                    return; default is 1
            limit:                  maximum number of records to return;
                                    maximum is 50, default is 10
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object

        """
        if not q:
            raise TypeError("Argument 'q' is requried to construct query.")

        url = self._url_search_brief_bibs()
        header = {"Accept": "application/json"}
        payload = {
            "q": q,
            "deweyNumber": deweyNumber,
            "datePublished": datePublished,
            "heldByGroup": heldByGroup,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "inLanguage": inLanguage,
            "inCatalogLanguage": inCatalogLanguage,
            "materialType": materialType,
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
            "groupRelatedEditions": groupRelatedEditions,
            "groupVariantRecords": groupVariantRecords,
            "preferredLanguage": preferredLanguage,
            "showHoldingsIndicators": showHoldingsIndicators,
            "lat": lat,
            "lon": lon,
            "distance": distance,
            "unit": unit,
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

    def search_brief_bibs_other_editions(
        self,
        oclcNumber: Union[int, str],
        deweyNumber: Optional[List[str]] = None,
        datePublished: Optional[List[str]] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[List[str]] = None,
        heldByInstitutionID: Optional[Union[int]] = None,
        inLanguage: Optional[str] = None,
        inCatalogLanguage: Optional[str] = None,
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[List[str]] = None,
        itemSubType: Optional[List[str]] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[List[str]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[List[str]] = None,
        groupVariantRecords: Optional[bool] = None,
        preferredLanguage: Optional[str] = None,
        showHoldingsIndicators: Optional[bool] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        orderBy: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC number.
        Uses /search/brief-bibs/{oclcNumber}/other-editions endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            deweyNumber:            limits the response to the
                                    specified dewey classification number(s);
                                    examples:
                                        '794,180'
                                        '794'
            datePublished:          limits the response to one or more dates or ranges
                                    examples:
                                        '2000'
                                        '2000-2005'
                                        '2000,2005'
                                        '2000-2002,2003-2005'
            heldByGroup:            restricts response to holdings held by group symbol
            heldBySymbol:           restricts response to holdings held by specified
                                    institution symbol
            heldByInstitutionID:    restricts response to holdings held by specified
                                    institution registryId
            inLanguage:             restricts response to the single
                                    specified language, example: 'fre'
            inCataloglanguage:      restricts response to specified
                                    cataloging language, example: 'eng';
                                    default is 'eng'
            materialType:           restricts response to specified material type,
                                    example: 'bks', 'vis'
            catalogSource:          restricts response to single OCLC symbol as
                                    the cataloging source, example: 'DLC'
            itemType:               restricts reponses to single specified OCLC
                                    top-level facet type, example: 'book'
            itemSubType:            restricts response to single specified OCLC
                                    sub facet type, example: 'digital'
            retentionCommitments:   restricts response to bibliographic records
                                    with retention commitment; options: True, False,
                                    default is False
            spProgram:              restricts response to bibliographic records
                                    associated with particular shared print
                                    program
            genre:                  genre to limit results to (ge index)
            topic:                  topic to limit results to (s0 index)
            subtopic:               subtopic to limit results to (s1 index)
            audience:               audience to limit results to,
                                    available values: "juv", 'nonJuv'
            content:                content to limit results to
                                    available values: 'fic', 'nonFic', 'bio'
            openAccess:             restricts response to just open access content
            peerReviewed:           restricts response to just peer reviewed content
            facets:                 list of facets requested in response
                                    available values: 'subject', 'creator',
                                    'datePublished', 'genre', 'itemType',
                                    'itemSubTypeBrief', 'itemSubType', 'language',
                                    'topic', 'subtopic', 'content', 'audience',
                                    'databases'
            groupVariantRecords:    whether or not to group variant records.
                                    options: True, False, default is False
            preferredLanguage:      language of metadata description,
                                    default is 'en' (English)
            showHoldingsIndicators: whether or not to show holdings indicators in
                                    response. options: True, False, default is False
            offset:                 start position of bibliographic records to
                                    return; default is 1
            limit:                  maximum nuber of records to return;
                                    maximum is 50, default is 10
            orderBy:                results sort key;
                                    options:
                                        'library'
                                        'recency'
                                        'bestMatch'
                                        'creator'
                                        'publicationDateAsc'
                                        'publicationDateDesc'
                                        'mostWidelyHeld'
                                        'title'
                                    default is bestMatch
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_brief_bibs_other_editions(oclcNumber)
        header = {"Accept": "application/json"}
        payload = {
            "deweyNumber": deweyNumber,
            "datePublished": datePublished,
            "heldByGroup": heldByGroup,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "inLanguage": inLanguage,
            "inCatalogLanguage": inCatalogLanguage,
            "materialType": materialType,
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
            "showHoldingsIndicators": showHoldingsIndicators,
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

    def search_shared_print_holdings(
        self,
        oclcNumber: Optional[Union[int, str]] = None,
        isbn: Optional[str] = None,
        issn: Optional[str] = None,
        heldByGroup: Optional[str] = None,
        heldInState: Optional[str] = None,
        itemType: Optional[List[str]] = None,
        itemSubType: Optional[List[str]] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Finds member shared print holdings for specified item.
        Uses /search/bibs-retained-holdings endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            isbn:                   ISBN without hyphen,
                                    example: '978149191646x'
            issn:                   ISSN with hyphen, example: '0099-1234'
            heldByGroup:            limits to holdings held by institutions
                                    indicated by group symbol
            heldInState:            limits to holdings held by institutions in
                                    requested state, example: 'US-NY'
            itemType:               limits results to specified item type
                                    examples: 'book' or 'vis'
            itemSubType:            limits results to specified item sub type
                                    examples: 'book-digital' or 'audiobook-cd'
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

        url = self._url_search_shared_print_holdings()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "isbn": isbn,
            "issn": issn,
            "heldByGroup": heldByGroup,
            "heldInState": heldInState,
            "itemType": itemType,
            "itemSubType": itemSubType,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def set_holding(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a MARC record in MARC XML or MARC21, set a holding on the record.
        MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.
        Uses /manage/institution/holdings/set/ endpoint.

        Args:
            record:                 MARC record on which to set holdings
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if not record:
            raise TypeError("Argument 'record' is missing.")
        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")

        url = self._url_manage_ih_set()
        header = {
            "Accept": "application/json",
            "content-type": recordFormat,
        }

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def set_holding_oclc_number(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC Number, set a holding on the record.
        Uses /manage/institution/holdings/{oclcNumber}/set/ endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_ih_oclc_number_set(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("POST", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def unset_holding(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a MARC record in MARC XML or MARC21, unset a holding on the record.
        MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.

        Args:
            record:                 MARC record on which to unset holdings
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if not record:
            raise TypeError("Argument 'record' is missing.")
        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")

        url = self._url_manage_ih_unset()
        header = {
            "Accept": "application/json",
            "content-type": recordFormat,
        }

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

    def unset_holding_oclc_number(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC Number, unset a holding on the record.
        Uses /manage/institution/holdings/{oclcNumber}/unset/ endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_ih_oclc_number_unset(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("POST", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def validate_bib(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        validationLevel: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a bib record, validate that record conforms to MARC standards
        Uses /manage/bibs/validate/{validationLevel} endpoint.

        Args:
            record:                 MARC record to be validated
            recordFormat:           format of MARC record, options:
                                    'application/marcxml+xml', 'application/marc'
            validationLevel:        Level at which to validate records
                                    available values: 'validateFull', 'validateAdd',
                                    'validateReplace'
                                    default is 'validateFull'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        if not record:
            raise TypeError("Argument 'record' is missing.")

        if not recordFormat:
            raise TypeError("Argument 'recordFormat' is missing.")

        if not validationLevel:
            validationLevel = "validateFull"

        url = self._url_manage_bib_validate(validationLevel)
        header = {
            "Accept": "application/json",
            "content-type": recordFormat,
        }

        # prep request
        req = Request(
            "POST",
            url,
            data=record,
            headers=header,
            hooks=hooks,
        )
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response
