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
        total_retries: int = 0,
        backoff_factor: float = 0,
        status_forcelist: Optional[List[int]] = [],
        allowed_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            authorization:          WorldcatAccessToken object
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 5 seconds
            total_retries:          optional number of times to retry a request that
                                    failed or timed out. if total_retries argument is
                                    not passed, any arguments passed to
                                    backoff_factor, status_forcelist, and
                                    allowed_methods will be ignored. default is 0
            backoff_factor:         if total_retries is not 0, the backoff
                                    factor as a float to use to calculate amount of
                                    time session will sleep before attempting request
                                    again. default is 0
            status_forcelist:       if total_retries is not 0, a list of HTTP
                                    status codes to automatically retry requests on.
                                    if not specified, all failed requests will be
                                    retried up to number of total_retries.
                                    example: [500, 502, 503, 504]
            allowed_methods:        if total_retries is not 0, set of HTTP methods that
                                    requests should be retried on. if not specified,
                                    requests using any HTTP method verbs will be
                                    retried. example: ["GET", "POST"]
        """
        super().__init__(
            authorization,
            agent=agent,
            timeout=timeout,
            total_retries=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=allowed_methods,
        )

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

    def _url_manage_bibs_validate(self, validationLevel: str) -> str:
        return f"{self.BASE_URL}/manage/bibs/validate/{validationLevel}"

    def _url_manage_bibs_current_oclc_number(self) -> str:
        return f"{self.BASE_URL}/manage/bibs/current"

    def _url_manage_bibs_create(self) -> str:
        return f"{self.BASE_URL}/manage/bibs"

    def _url_manage_bibs(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/bibs/{oclcNumber}"

    def _url_manage_bibs_match(self) -> str:
        return f"{self.BASE_URL}/manage/bibs/match"

    def _url_manage_ih_current(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/current"

    def _url_manage_ih_set(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/{oclcNumber}/set"

    def _url_manage_ih_unset(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/{oclcNumber}/unset"

    def _url_manage_ih_set_on_bib(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/set"

    def _url_manage_ih_unset_on_bib(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/unset"

    def _url_manage_ih_codes(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holding-codes"

    def _url_manage_lbd_create(self) -> str:
        return f"{self.BASE_URL}/manage/lbds"

    def _url_manage_lbd(self, controlNumber: Union[str, int]) -> str:
        return f"{self.BASE_URL}/manage/lbds/{controlNumber}"

    def _url_manage_lhr_create(self) -> str:
        return f"{self.BASE_URL}/manage/lhrs"

    def _url_manage_lhr(self, controlNumber: Union[str, int]) -> str:
        return f"{self.BASE_URL}/manage/lhrs/{controlNumber}"

    def _url_search_shared_print_holdings(self) -> str:
        return f"{self.BASE_URL}/search/bibs-retained-holdings"

    def _url_search_general_holdings(self) -> str:
        return f"{self.BASE_URL}/search/bibs-summary-holdings"

    def _url_search_general_holdings_summary(self) -> str:
        return f"{self.BASE_URL}/search/summary-holdings"

    def _url_search_brief_bibs(self) -> str:
        return f"{self.BASE_URL}/search/brief-bibs"

    def _url_search_brief_bibs_oclc_number(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}"

    def _url_search_brief_bibs_other_editions(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}/other-editions"

    def _url_search_classification_bibs(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/classification-bibs/{oclcNumber}"

    def _url_search_lhr_shared_print(self) -> str:
        return f"{self.BASE_URL}/search/retained-holdings"

    def _url_search_lhr_control_number(self, controlNumber: Union[str, int]) -> str:
        return f"{self.BASE_URL}/search/my-holdings/{controlNumber}"

    def _url_search_lhr(self) -> str:
        return f"{self.BASE_URL}/search/my-holdings"

    def _url_browse_lhr(self) -> str:
        return f"{self.BASE_URL}/browse/my-holdings"

    def _url_search_lbd_control_number(self, controlNumber: Union[str, int]) -> str:
        return f"{self.BASE_URL}/search/my-local-bib-data/{controlNumber}"

    def _url_search_lbd(self) -> str:
        return f"{self.BASE_URL}/search/my-local-bib-data"

    def bib_create(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Create a bib record in OCLC if it does not already exist
        Uses /manage/bibs endpoint.

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

        url = self._url_manage_bibs_create()
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

    def bib_get(
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

    def bib_get_classification(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number, retrieve classification recommendations for the bib record
        Uses /search/classification-bibs/{oclcNumber} endpoint.

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

    def bib_get_current_oclc_number(
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

    def bib_match(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a bib record in MARC21 or MARCXML identify the best match in WorldCat.
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

        url = self._url_manage_bibs_match()
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

    def bib_replace(
        self,
        oclcNumber: Union[int, str],
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number and MARC record, find record in WorldCat and replace it.
        If the record does not exist in WorldCat, a new bib record will be created.
        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number for record to be
                                    replaced; can be an integer or string with or
                                    without OCLC # prefix
            record:                 MARC record to replace existing WorldCat record
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

        url = self._url_manage_bibs(oclcNumber)
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

    def bib_validate(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        validationLevel: str = "validateFull",
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

        url = self._url_manage_bibs_validate(validationLevel)
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

    def brief_bibs_get(
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

    def brief_bibs_search(
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
            limit:                  maximum number of records to return;
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

    def brief_bibs_search_other_editions(
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
            heldByInstitutionID:    restrict to specified institution registryId
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
            limit:                  maximum number of records to return;
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

    def holdings_get_codes(
        self,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve the all holding codes for the authenticated institution.
        Uses /manage/institution/holding-codes endpoint.

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

    def holdings_get_current(
        self,
        oclcNumbers: Union[str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> List[Response]:
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

    def holdings_set(
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

    def holdings_unset(
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

    def holdings_set_on_bib(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a MARC record in MARC XML or MARC21, set a holding on the record.
        MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.
        Uses /manage/institution/holdings/set endpoint.

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

        url = self._url_manage_ih_set_on_bib()
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

    def holdings_unset_on_bib(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a MARC record in MARC XML or MARC21, unset a holding on the record.
        MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.
        Uses /manage/institution/holdings/unset endpoint.

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

        url = self._url_manage_ih_unset_on_bib()
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

    def lbd_create(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a local bibliographic data record, create it in WorldCat
        Uses /manage/lbds endpoint.

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

        url = self._url_manage_lbd_create()
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

    def lbd_delete(
        self,
        controlNumber: Union[int, str],
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a control number, delete the associated Local Bibliographic Data record
        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Bibliographic
                                    Data record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_manage_lbd(controlNumber)
        header = {"Accept": responseFormat}

        # prep request
        req = Request("DELETE", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lbd_get(
        self,
        controlNumber: Union[int, str],
        response_format: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a Control Number, retrieve a Local Bibliographic Data record.
        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Bibliographic
                                    Data record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_manage_lbd(controlNumber)
        header = {"Accept": response_format}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lbd_replace(
        self,
        controlNumber: Union[int, str],
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a Control Number, find the associated Local Bibliographic Data
        Record and replace it. If the Control Number is not found in
        WorldCat, then the provided Local Bibliographic Data Record will be created.
        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Bibliographic
                                    Data record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
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

        url = self._url_manage_lbd(controlNumber)
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

    def lhr_create(
        self,
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a local holdings record, create it in WorldCat
        Uses /manage/lhrs endpoint.

        Args:
            record:                 Holdings record to be created
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

        url = self._url_manage_lhr_create()
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

    def lhr_delete(
        self,
        controlNumber: Union[int, str],
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a control number, delete a Local Holdings record.
        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Holdings
                                    record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_manage_lhr(controlNumber)
        header = {"Accept": responseFormat}

        # prep request
        req = Request("DELETE", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lhr_get(
        self,
        controlNumber: Union[int, str],
        response_format: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Send a GET request for a local holdings record
        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Holdings
                                    record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_manage_lhr(controlNumber)
        header = {"Accept": response_format}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lhr_replace(
        self,
        controlNumber: Union[int, str],
        record: Optional[str] = None,
        recordFormat: Optional[str] = None,
        responseFormat: Optional[str] = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a Control Number, find the associated Local Holdings
        Record and replace it. If the Control Number is not found in
        WorldCat, then the provided Local Holdings Record will be created.
        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Holdings
                                    record; can be an integer, or string
            response_format:        format of returned record, options:
                                    'application/marcxml+xml', 'application/marc',
                                    default is 'application/marcxml+xml'
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

        url = self._url_manage_lhr(controlNumber)
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

    def local_bibs_get(
        self,
        controlNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve LBD Resource
        Uses /search/my-local-bib-data/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Bibliographic
                                    Data record; can be an integer, or string
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_search_lbd_control_number(controlNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def local_bibs_search(
        self,
        q: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Search LBD Resources
        Uses /search/my-local-bib-data endpoint.

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
            offset:                 start position of bibliographic records to
                                    return; default is 1
            limit:                  maximum number of records to return;
                                    maximum is 50, default is 10
            hooks:                  Requests library hook system that can be used for
                                    signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if not q:
            raise TypeError("Argument 'q' is requried to construct query.")

        url = self._url_search_lbd()
        header = {"Accept": "application/json"}
        payload = {"q": q, "offset": offset, "limit": limit}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def local_holdings_browse(
        self,
        callNumber: Optional[str] = None,
        oclcNumber: Optional[Union[int, str]] = None,
        holdingLocation: str = "",
        shelvingLocation: str = "",
        browsePosition: Optional[str] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Browse local holdings
        Uses /browse/my-holdings endpoint.

        Args:
            callNumber:             call number for item
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer or string with or without OCLC #
                                    prefix
            holdingLocation:        holding location for item
            shelvingLocation:       shelving location for item
            browsePosition:         position within browse list where the matching
                                    record should be, default is 10
            limit:                  maximum number of records to return;
                                    maximum 50, default 10
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        if not holdingLocation:
            raise TypeError("Argument 'holdingLocation' is missing.")
        if not shelvingLocation:
            raise TypeError("Argument 'shelvingLocation' is missing.")

        if oclcNumber is not None:
            oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_browse_lhr()
        header = {"Accept": "application/json"}
        payload = {
            "callNumber": callNumber,
            "oclcNumber": oclcNumber,
            "holdingLocation": holdingLocation,
            "shelvingLocation": shelvingLocation,
            "browsePosition": browsePosition,
            "limit": limit,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def local_holdings_get(
        self,
        controlNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve LHR Resource
        Uses /search/my-holdings/{controlNumber} endpoint.

        Args:
            controlNumber:          control number associated with Local Holdings
                                    record; can be an integer, or string
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        url = self._url_search_lhr_control_number(controlNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def local_holdings_search(
        self,
        oclcNumber: Optional[Union[int, str]] = None,
        barcode: Optional[str] = None,
        orderBy: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Search LHR Resources
        Uses /search/my-holdings endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            barcode:                barcode as a string,
            orderBy:                results sort key;
                                    options:
                                        'commitmentExpirationDate'
                                        'location'
                                        'oclcSymbol'
                                    default is 'oclcSymbol'
            offset:                 start position of bibliographic records to
                                    return; default is 1
            limit:                  maximum number of records to return;
                                    maximum is 50, default is 10
            hooks:                  Requests library hook system that can be used for
                                    signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if oclcNumber is not None:
            oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_lhr()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "barcode": barcode,
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

    def local_holdings_search_shared_print(
        self,
        oclcNumber: Optional[Union[int, str]] = None,
        barcode: Optional[str] = None,
        heldBySymbol: Optional[List[str]] = None,
        heldByInstitutionID: Optional[List[int]] = None,
        spProgram: Optional[List[str]] = None,
        orderBy: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Search for shared print LHR Resources
        Uses /search/retained-holdings endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be
                                    an integer, or string that can include
                                    OCLC # prefix
            barcode:                barcode as a string,
            heldBySymbol:           restricts to holdings with specified intitution
                                    symbol
            heldByInstitutionID:    restrict to specified institution registryId
            spProgram:              restricts responses to bibliographic records
                                    associated with particular shared print
                                    program
            orderBy:                results sort key;
                                    options:
                                        'commitmentExpirationDate'
                                        'location'
                                        'oclcSymbol'
                                    default is 'oclcSymbol'
            offset:                 start position of bibliographic records to
                                    return; default is 1
            limit:                  maximum number of records to return;
                                    maximum is 50, default is 10
            hooks:                  Requests library hook system that can be used for
                                    signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if oclcNumber is not None:
            oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_lhr_shared_print()
        header = {"Accept": "application/json"}
        payload = {
            "oclcNumber": oclcNumber,
            "barcode": barcode,
            "heldBySymbol": heldBySymbol,
            "heldByInstitutionID": heldByInstitutionID,
            "spProgram": spProgram,
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

    def shared_print_holdings_search(
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

    def summary_holdings_search(
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

    def summary_holdings_get(
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
        Uses /search/summary-holdings endpoint.

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
