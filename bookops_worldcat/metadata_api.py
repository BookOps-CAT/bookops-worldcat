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

    BASE_URL = "https://metadata.api.oclc.org/worldcat"

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

    def _url_manage_bibs(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/bibs/{oclcNumber}"

    def _url_manage_bibs_current_oclc_number(self) -> str:
        return f"{self.BASE_URL}/manage/bibs/current"

    def _url_manage_ih_current(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/current"

    def _url_manage_ih_set(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/{oclcNumber}/set"

    def _url_manage_ih_unset(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/{oclcNumber}/unset"

    def _url_search_shared_print_holdings(self) -> str:
        return f"{self.BASE_URL}/search/bibs-retained-holdings"

    def _url_search_general_holdings(self) -> str:
        return f"{self.BASE_URL}/search/bibs-summary-holdings"

    def _url_search_brief_bibs(self) -> str:
        return f"{self.BASE_URL}/search/brief-bibs"

    def _url_search_brief_bibs_oclc_number(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}"

    def _url_search_brief_bibs_other_editions(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}/other-editions"

    def _url_lhr_shared_print(self) -> str:
        return f"{self.BASE_URL}/retained-holdings"

    def _url_lhr_control_number(self, controlNumber: str) -> str:
        return f"{self.BASE_URL}/my-holdings/{controlNumber}"

    def _url_lhr_search(self) -> str:
        return f"{self.BASE_URL}/my-holdings"

    def get_brief_bib(
        self, oclcNumber: Union[int, str], hooks: Optional[Dict[str, Callable]] = None
    ) -> Optional[Response]:
        """
        Retrieve specific brief bibliographic resource.
        Uses /search/brief-bibs/{oclcNumber} endpoint.

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
        Retrieve current OCLC control numbers
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
            `requests.Response` object
        """

        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        header = {"Accept": "application/json"}
        url = self._url_manage_bibs_current_oclc_number()
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
        response_format: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Send a GET request for a full bibliographic resource.
        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_bibs(oclcNumber)
        header = {"Accept": response_format}

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
    ) -> List[Optional[Response]]:
        """
        Retrieves Worlcat holdings status of a record with provided OCLC number.
        The service automatically recognizes institution based on the issued access
        token.
        Uses /manage/institution/holdings/current endpoint.

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
        responses = []
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        url = self._url_manage_ih_current()
        header = {"Accept": "application/json"}

        for batch in self._split_into_legal_volume(oclc_numbers=vetted_numbers, n=10):
            payload = {"oclcNumbers": batch}

            # prep request
            req = Request("GET", url, params=payload, headers=header, hooks=hooks)
            prepared_request = self.prepare_request(req)

            # send request
            query = Query(self, prepared_request, timeout=self.timeout)
            responses.append(query.response)

        return responses

    def holding_set(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Sets institution's Worldcat holding on an individual record.
        Uses /manage/institions/holdings/{oclcNumber}/set endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_ih_set(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("POST", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holding_unset(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Deletes institution's Worldcat holding on an individual record.
        Uses /manage/institions/holdings/{oclcNumber}/unset endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
                                    if str the numbers must be separated by comma
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_ih_unset(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("POST", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_brief_bibs(
        self,
        q: str,
        deweyNumber: Optional[Union[str, List[str]]] = None,
        datePublished: Optional[Union[str, List[str]]] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[Union[str, List[str]]] = None,
        heldByInstitutionID: Optional[Union[str, int, List[str], List[int]]] = None,
        inLanguage: Optional[Union[str, List[str]]] = None,
        inCatalogLanguage: Optional[str] = None,
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[Union[str, List[str]]] = None,
        itemSubType: Optional[Union[str, List[str]]] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[Union[str, List[str]]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[Union[str, List[str]]] = None,
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
        Send a GET request for brief bibliographic resources.
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
            heldBySymbol:           restricts response to holdings held by specified
                                    institution symbol
            heldByInstitutionID:    restricts response to holdings held by specified
                                    institution registryId
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
            genre:                  genre to limit results to (ge index)
            topic:                  topic to limit results to (s0 index)
            subtopic:               subtopic to limit results to (s1 index)
            audience:               audience to limit results to,
                                    available values: 'juv', 'nonJuv'
            content:                content to limit results to
                                    available values: 'fic', 'nonFic', 'bio'
            openAccess:             restricts response to just open access content
            peerReviewed:           restricts response to just peer reviewed content
            facets:                 list of facets to restrict responses
            groupRelatedEditions:   whether or not use FRBR grouping,
                                    options: False, True (default is False)
            groupVariantRecords:    whether or not to group variant records.
                                    options: False, True (default False)
            preferredLanguage:      language of metadata description,
                                    default value "en" (English)
            showHoldingsIndicators: whether or not to show holdings indicators in
                                    response. options: True, False, default is False
            lat:                    limit to latitude, example: 37.502508
            lon:                    limit to longitute, example: -122.22702
            distance:               distance from latitude and longitude
            unit:                   unit of distance param; options:
                                    'M' (miles) or 'K' (kilometers)
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
        deweyNumber: Optional[Union[str, List[str]]] = None,
        datePublished: Optional[Union[str, List[str]]] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[Union[str, List[str]]] = None,
        heldByInstitutionID: Optional[Union[str, int, List[Union[str, int]]]] = None,
        inLanguage: Optional[Union[str, List[str]]] = None,
        inCatalogLanguage: Optional[str] = None,
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[Union[str, List[str]]] = None,
        itemSubType: Optional[Union[str, List[str]]] = None,
        retentionCommitments: Optional[bool] = None,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[Union[str, List[str]]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[Union[str, List[str]]] = None,
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
        OCLC #.
        Uses /brief-bibs/{oclcNumber}/other-editions endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            deweyNumber:            limits the response to the
                                    specified dewey classification number(s)
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

    def search_bibs_holdings(
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
            holdingsFilterFormat:       get holdings for specific itemSubType,
                                        example: book-digital
            heldInCountry:              restricts to holdings held by institutions
                                        in requested country
            heldInState:                limits to holdings held by institutions
                                        in requested state, example: 'US-NY'
            heldByGroup:                limits to holdings held by indicated by
                                        symbol group
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
            hooks:                  Requests library hook system that can be used for
                                    signal event handling, see more at:
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
