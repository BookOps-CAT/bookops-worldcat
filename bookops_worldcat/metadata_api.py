# -*- coding: utf-8 -*-

"""WorldCat Metadata API wrapper session."""

from typing import BinaryIO, Callable, Dict, List, Optional, Tuple, Union

from requests import Request, Response

from ._session import WorldcatSession
from .authorize import WorldcatAccessToken
from .query import Query
from .utils import verify_ids, verify_oclc_number, verify_oclc_numbers


class MetadataSession(WorldcatSession):
    """
    The `MetadataSession` class supports interactions with the WorldCat Metadata API
    and the child methods of this class allow users to interact with each endpoint
    of the API.

    `MetadataSession` inherits attributes and methods from `requests.Session`
    and `WorldcatSession` and contains specific functionality for interacting
    with the WorldCat Metadata API.
    """

    BASE_URL = "https://metadata.api.oclc.org/worldcat"

    def __init__(
        self,
        authorization: WorldcatAccessToken,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            5,
            5,
        ),
        totalRetries: int = 0,
        backoffFactor: float = 0,
        statusForcelist: Optional[List[int]] = None,
        allowedMethods: Optional[List[str]] = None,
    ) -> None:
        """Initializes MetadataSession.

        Args:
            authorization:
                `WorldcatAccessToken` object for session.
            agent:
                `User-agent` for session to be passed in the request header. Usage is
                strongly encouraged.
            timeout:
                How long to wait for server to send data before giving up. Accepts
                separate values for connect and read timeouts or a single value.
            totalRetries:
                Optional number of times to retry a request that failed or timed out.
                If `totalRetries` argument is not passed, any arguments passed to
                `backoffFactor`, `statusForcelist`, and `allowedMethods` will be
                ignored.
            backoffFactor:
                If `totalRetries` is not `0`, the backoff factor as a float to use to
                calculate amount of time session will sleep before attempting request
                again.
            statusForcelist:
                If `totalRetries` is not `0`, a list of HTTP status codes to
                automatically retry requests on. If not specified, failed requests
                with status codes 413, 429, and 503 will be retried up to number of
                `totalRetries`.

                **EXAMPLE:** `[500, 502, 503, 504]`
            allowedMethods:
                If `totalRetries` is not `0`, set of HTTP methods that requests should
                be retried on. If not specified, requests using any HTTP method verbs
                will be retried.

                **EXAMPLE:** `["GET", "POST"]`
        """
        super().__init__(
            authorization,
            agent=agent,
            timeout=timeout,
            totalRetries=totalRetries,
            backoffFactor=backoffFactor,
            statusForcelist=statusForcelist,
            allowedMethods=allowedMethods,
        )

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

    def _url_manage_ih_set_with_bib(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/set"

    def _url_manage_ih_unset_with_bib(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holdings/unset"

    def _url_manage_ih_codes(self) -> str:
        return f"{self.BASE_URL}/manage/institution/holding-codes"

    def _url_manage_institution_config(self) -> str:
        return f"{self.BASE_URL}/manage/institution-config/branch-shelving-locations"

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

    def _url_search_bibs(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/bibs/{oclcNumber}"

    def _url_search_brief_bibs(self) -> str:
        return f"{self.BASE_URL}/search/brief-bibs"

    def _url_search_brief_bibs_oclc_number(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}"

    def _url_search_brief_bibs_other_editions(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/brief-bibs/{oclcNumber}/other-editions"

    def _url_search_classification_bibs(self, oclcNumber: str) -> str:
        return f"{self.BASE_URL}/search/classification-bibs/{oclcNumber}"

    def _url_search_institution(self) -> str:
        return f"{self.BASE_URL}/search/institution"

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
        record: Union[str, bytes, BinaryIO],
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Create a bib record in OCLC if it does not already exist.

        Uses /manage/bibs endpoint.

        Args:
            record:
                MARC record to be created
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Send a GET request for a full bib record.

        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_bibs(oclcNumber)
        header = {"Accept": responseFormat}

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
    ) -> Response:
        """
        Given an OCLC number, retrieve classification recommendations for the bib
        record.

        Uses /search/classification-bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        oclcNumbers: Union[int, str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given one or more OCLC Numbers, retrieve current OCLC numbers.

        Uses /manage/bibs/current endpoint.

        Args:
            oclcNumbers:
                Integer, string or list containing one or more OCLC numbers to be
                checked. Numbers can be integers or strings with or without OCLC
                Number prefix. If str, the numbers must be separated by a comma.
                If int, only one number may be passed as an arg.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Raises:
            ValueError: If more than 10 items passed to `oclcNumbers` arg.
        """
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        # check that no more than 10 oclc numbers were passed
        if len(vetted_numbers) > 10:
            raise ValueError("Too many OCLC Numbers passed to 'oclcNumbers' argument.")

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
        record: Union[str, bytes, BinaryIO],
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a bib record in MARC21 or MARCXML identify the best match in WorldCat.
        Record must contain at minimum an 008 and 245. Response contains number of
        potential matches in `numberOfRecords` and best match in `briefRecords`.

        Uses /manage/bibs/match endpoint.

        Args:
            record:
                MARC record to be matched.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        record: Union[str, bytes, BinaryIO],
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given an OCLC number and MARC record, find record in WorldCat and replace it.
        If the record does not exist in WorldCat, a new bib record will be created.

        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            record:
                MARC record to replace existing WorldCat record
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

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

    def bib_search(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Send a GET request for a full bib record in JSON format.

        Uses /search/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_search_bibs(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def bib_validate(
        self,
        record: Union[str, bytes, BinaryIO],
        recordFormat: str,
        validationLevel: str = "validateFull",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a bib record, validate that record conforms to MARC standards.

        Uses /manage/bibs/validate/{validationLevel} endpoint.

        Args:
            record:
                MARC record to validate
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            validationLevel:
                Level at which to validate records.

                **OPTIONS:** `'validateFull'`, `'validateAdd'`, `'validateReplace'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance

        Raises:
            ValueError:
                If value of arg passed to `validationLevel` is not
                `'validateFull'`, `'validateAdd'`, or `'validateReplace'`.
        """
        if validationLevel not in ["validateFull", "validateAdd", "validateReplace"]:
            raise ValueError(
                "Invalid argument 'validationLevel'."
                "Must be either 'validateFull', 'validateAdd', or 'validateReplace'"
            )

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

    def branch_holding_codes_get(
        self,
        includeShelvingLocations: bool = False,
        branchLocationLimit: Optional[int] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Retrieve branch holding codes or shelving locations for the authenticated
        institution.

        Uses /manage/institution-config/branch-shelving-locations endpoint.

        Args:
            branchLocationLimit:
                Limits response to branch locations associated with a specific
                registryId.
            includeShelvingLocations:
                Whether or not to include shelving location information in response.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """

        url = self._url_manage_institution_config()
        header = {"Accept": "application/json"}

        payload = {
            "branchLocationLimit": branchLocationLimit,
            "includeShelvingLocations": includeShelvingLocations,
        }

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def brief_bibs_get(
        self, oclcNumber: Union[int, str], hooks: Optional[Dict[str, Callable]] = None
    ) -> Response:
        """
        Retrieve specific brief bibliographic resource.

        Uses /search/brief-bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

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
        inCatalogLanguage: Optional[str] = "eng",
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[Union[str, List[str]]] = None,
        itemSubType: Optional[Union[str, List[str]]] = None,
        retentionCommitments: bool = False,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[Union[str, List[str]]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[Union[str, List[str]]] = None,
        groupRelatedEditions: bool = False,
        groupVariantRecords: bool = False,
        preferredLanguage: str = "eng",
        showHoldingsIndicators: bool = False,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        distance: Optional[int] = None,
        unit: str = "M",
        orderBy: str = "bestMatch",
        offset: int = 1,
        limit: int = 10,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Search for brief bibliographic resources using WorldCat query syntax.
        See OCLC
        [Bibliographic Records Index Documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Bibliographic_records/Bibliographic_record_indexes)
        for more information on available indexes. Request may contain
        only one of: `heldByInstitutionID`, `heldByGroup`, `heldBySymbol`, or
        combination of `lat` and `lon`.

        Uses /search/brief-bibs endpoint.

        Args:
            q:
                Query in the form of a keyword search or fielded search.

                **EXAMPLES:**

                - `ti:Zendegi`
                - `ti:"Czarne oceany"`
                - `bn:9781680502404`
                - `kw:python databases`
                - `ti:Zendegi AND au:greg egan`
                - `(au:Okken OR au:Myers) AND su:python`

            deweyNumber:
                Limits the response to the specified dewey classification number(s).
                For multiple values repeat the parameter.

                **EXAMPLE:** `'794'`
            datePublished:
                Restricts the response to one or more dates, or to a range.

                **EXAMPLES:** `'2000'`, `'2000-2005'`, `'2000,2005'`
            heldByGroup:
                Limits response to holdings held by group symbol.
            heldBySymbol:
                Limits response to holdings held by specified institution symbol.
            heldByInstitutionID:
                Limits response to holdings held by specified institution registryId.
            inLanguage:
                Limits response to the single specified language

                **EXAMPLE:** `'fre'`
            inCatalogLanguage:
                Limits response to specified cataloging language.

                **EXAMPLE:** `'eng'`
            materialType:
                Limits response to specified material type.

                **EXAMPLES:** `'bks'`, `'vis'`
            catalogSource:
                Limits response to single OCLC symbol as the cataloging source.

                **EXAMPLE:** `'DLC'`
            itemType:
                Limits response to specified item type.

                **EXAMPLE:** `'book'`, `'vis'`
            itemSubType:
                Limits response to specified item subtype.

                **EXAMPLES:** `'book-digital'`, `'audiobook-cd'`
            retentionCommitments:
                Limits response to bibliographic records with retention commitment.

                **OPTIONS:** `True` or `False`
            spProgram:
                Limits response to bibliographic records associated with particular
                shared print program.
            genre:
                Genre to limit response to (ge index).
            topic:
                Topic to limit response to (s0 index).
            subtopic:
                Subtopic to limit response to (s1 index).
            audience:
                Audience to limit response to.

                **OPTIONS:** `'juv'` or `'nonJuv'`
            content:
                Content to limit response to.

                **OPTIONS:** `'fic'`, `'nonFic'`, `'bio'`
            openAccess:
                Limits response to just open access content.
            peerReviewed:
                Limits response to just peer reviewed content.
            facets:
                List of facets to limit responses.
            groupRelatedEditions:
                Whether or not use FRBR grouping.

                **OPTIONS:** `True` or `False`
            groupVariantRecords:
                Whether or not to group variant records.

                **OPTIONS:** `True` or `False`
            preferredLanguage:
                Language user would prefer metadata description in. Does not limit
                responses. To limit responses use `inCataloglanguage` facet.
            showHoldingsIndicators:
                Whether or not to show holdings indicators in response.
                **OPTIONS:** `True` or `False`
            lat:
                Latitude

                **EXAMPLE:** `37.502508`
            lon:
                Longitude

                **EXAMPLE:** `-122.22702`
            distance:
                Limits response to holdings held by institutions within specified
                distance from latitude and longitude.
            unit:
                Unit of distance from latitude and longitude.

                **OPTIONS:** `'M'` (miles) or `'K'` (kilometers)
            orderBy:
                Results sort key.

                **OPTIONS:**

                - `'recency'`
                - `'bestMatch'`
                - `'creator'`
                - `'library'`
                - `'publicationDateAsc'`
                - `'publicationDateDesc'`
                - `'mostWidelyHeld'`
                - `'title'`
            offset:
                Start position of bibliographic records to return.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """  # noqa: E501
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

    def brief_bibs_get_other_editions(
        self,
        oclcNumber: Union[int, str],
        deweyNumber: Optional[Union[str, List[str]]] = None,
        datePublished: Optional[Union[str, List[str]]] = None,
        heldByGroup: Optional[str] = None,
        heldBySymbol: Optional[Union[str, List[str]]] = None,
        heldByInstitutionID: Optional[Union[str, int, List[Union[str, int]]]] = None,
        inLanguage: Optional[Union[str, List[str]]] = None,
        inCatalogLanguage: Optional[str] = "eng",
        materialType: Optional[str] = None,
        catalogSource: Optional[str] = None,
        itemType: Optional[Union[str, List[str]]] = None,
        itemSubType: Optional[Union[str, List[str]]] = None,
        retentionCommitments: bool = False,
        spProgram: Optional[str] = None,
        genre: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        audience: Optional[str] = None,
        content: Optional[Union[str, List[str]]] = None,
        openAccess: Optional[bool] = None,
        peerReviewed: Optional[bool] = None,
        facets: Optional[Union[str, List[str]]] = None,
        groupVariantRecords: bool = False,
        preferredLanguage: str = "eng",
        showHoldingsIndicators: bool = False,
        offset: int = 1,
        limit: int = 10,
        orderBy: str = "publicationDateDesc",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Retrieve other editions related to bibliographic resource with provided
        OCLC Number. Query may contain only one of: `heldByInstitutionID`,
        `heldByGroup`, `heldBySymbol`, or `spProgram`.

        Uses /brief-bibs/{oclcNumber}/other-editions endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            deweyNumber:
                Limits response to the specified dewey classification number(s).
                For multiple values repeat the parameter.

                **EXAMPLE:** `'794'`
            datePublished:
                Limits response to one or more dates, or to a range.

                **EXAMPLES:** `'2000'`, `'2000-2005'`, `'2000,2005'`
            heldByGroup:
                Limits response to holdings held by group symbol.
            heldBySymbol:
                Limits response to holdings held by specified institution symbol.
            heldByInstitutionID:
                Limits response to holdings held by specified institution registryId.
            inLanguage:
                Limits response to the single specified language

                **EXAMPLE:** `'fre'`
            inCatalogLanguage:
                Limits response to specified cataloging language.

                **EXAMPLE:** `'eng'`
            materialType:
                Limits response to specified material type.

                **EXAMPLES:** `'bks'`, `'vis'`
            catalogSource:
                Limits response to single OCLC symbol as the cataloging source.

                **EXAMPLE:** `'DLC'`
            itemType:
                Limits response to specified item type.

                **EXAMPLES:** `'book'`, `'vis'`
            itemSubType:
                Limits response to specified item sub type

                **EXAMPLES:** `'book-digital'`, `'audiobook-cd'`
            retentionCommitments:
                Limits response to bibliographic records with retention commitment.

                **OPTIONS:** `True` or `False`
            spProgram:
                Limits response to bibliographic records associated with particular
                shared print program.
            genre:
                Genre to limit response to (ge index).
            topic:
                Topic to limit response to (s0 index).
            subtopic:
                Subtopic to limit response to (s1 index).
            audience:
                Audience to limit response to.

                **OPTIONS:** `'juv'` or `'nonJuv'`
            content:
                Content to limit response to.

                **OPTIONS:** `'fic'`, `'nonFic'`, `'bio'`
            openAccess:
                Limits response to just open access content.
            peerReviewed:
                Limits response to just peer reviewed content.
            facets:
                List of facets to limit responses.
            groupVariantRecords:
                Whether or not to group variant records.

                **OPTIONS:** `True` or `False`
            preferredLanguage:
                Language user would prefer metadata description in. Does not limit
                responses. To limit responses use `inCataloglanguage` facet.
            showHoldingsIndicators:
                Whether or not to show holdings indicators in response.

                **OPTIONS:** `True` or `False`
            offset:
                Start position of bibliographic records to return.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            orderBy:
                Results sort key.

                **OPTIONS:**

                - `'recency'`
                - `'bestMatch'`
                - `'creator'`
                - `'library'`
                - `'publicationDateAsc'`
                - `'publicationDateDesc'`
                - `'mostWidelyHeld'`
                - `'title'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
    ) -> Response:
        """
        Retrieve the all holding codes for the authenticated institution.

        Uses /manage/institution/holding-codes endpoint.

        Args:
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        oclcNumbers: Union[int, str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Retrieves WorldCat holdings status of a record with provided OCLC number.
        The service automatically recognizes the user's institution based on the
        issued access token.

        Uses /manage/institution/holdings/current endpoint.

        Args:
            oclcNumbers:
                Integer, string or list containing one or more OCLC numbers to be
                checked. Numbers can be integers or strings with or without OCLC
                Number prefix. If str, the numbers must be separated by a comma.
                If int, only one number may be passed as an arg.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance

        Raises:
            ValueError: If more than 10 items passed to `oclcNumbers` arg.
        """
        vetted_numbers = verify_oclc_numbers(oclcNumbers)

        # check that no more than 10 oclc numbers were passed
        if len(vetted_numbers) > 10:
            raise ValueError("Too many OCLC Numbers passed to 'oclcNumbers' argument.")

        url = self._url_manage_ih_current()
        header = {"Accept": "application/json"}

        payload = {"oclcNumbers": vetted_numbers}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holdings_set(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Sets institution's WorldCat holdings on an individual record.

        Uses /manage/institions/holdings/{oclcNumber}/set endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        cascadeDelete: bool = True,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Unsets institution's WorldCat holdings on an individual record.

        Uses /manage/institions/holdings/{oclcNumber}/unset endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            cascadeDelete:
                Whether or not to remove any LBDs and/or LHRs associated with
                the bib record on which holdings are being removed. If `False`,
                associated local records will remain in WorldCat. If `True`,
                local records will be removed from WorldCat.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        url = self._url_manage_ih_unset(oclcNumber)
        header = {"Accept": "application/json"}

        payload = {"cascadeDelete": cascadeDelete}

        # prep request
        req = Request("POST", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holdings_set_with_bib(
        self,
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a MARC record in MARCXML or MARC21, set institution holdings on the
        record. MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.

        Uses /manage/institution/holdings/set endpoint.

        Args:
            record:
                MARC record on which to set holdings.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        url = self._url_manage_ih_set_with_bib()
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

    def holdings_unset_with_bib(
        self,
        record: str,
        recordFormat: str,
        cascadeDelete: bool = True,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a MARC record in MARCXML or MARC21, unset institution holdings on the
        record. MARC record must contain OCLC number in 001 or 035 subfield a.
        Only one MARC record is allowed in the request body.

        Uses /manage/institution/holdings/unset endpoint.

        Args:
            record:
                MARC record on which to unset holdings.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            cascadeDelete:
                Whether or not to remove any LBDs and/or LHRs associated with
                the bib record on which holdings are being removed. If `False`,
                associated local records will remain in WorldCat. If `True`,
                local records will be removed from WorldCat.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """

        url = self._url_manage_ih_unset_with_bib()
        header = {
            "Accept": "application/json",
            "content-type": recordFormat,
        }

        payload = {"cascadeDelete": cascadeDelete}

        # prep request
        req = Request(
            "POST",
            url,
            data=record,
            params=payload,
            headers=header,
            hooks=hooks,
        )
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

    def institution_indentifiers_get(
        self,
        registryIds: Optional[Union[str, int, List[str], List[int]]] = None,
        oclcSymbols: Optional[Union[str, List[str]]] = None,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Retrieve identifiers for an institution based on registry IDs or OCLC symbol.
        Query must contain either `registryIds` or `oclcSymbols` but not both.

        Uses /search/institution endpoint.

        Args:
            registryId:
                One or more registry IDs to retrieve identifiers for.
                May be a string, integer, or list of strings and/or integers.
                If a string, multiple IDs must be separated by a comma.

                **EXAMPLES:**

                - `58122`
                - `58122,12337`
                - `58122, 12337`
                - `['58122', '12337']`
            oclcSymbols:
                One or more OCLC symbols to retrieve identifiers for.
                May be a string or a list of strings. If a string, multiple
                symbols must be separated by a comma.

                **EXAMPLES:**

                - `NYP`
                - `NYP,BKL`
                - `NYP, BKL`
                - `['NYP', 'BKL']
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        url = self._url_search_institution()
        header = {"Accept": "application/json"}

        registry_ids = verify_ids(registryIds)
        oclc_symbols = verify_ids(oclcSymbols)
        payload = {"registryIds": registry_ids, "oclcSymbols": oclc_symbols}

        # prep request
        req = Request("GET", url, params=payload, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lbd_create(
        self,
        record: str,
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a local bibliographic data record, create it in WorldCat.

        Uses /manage/lbds endpoint.

        Args:
            record:
                MARC record to be created.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a control number, delete the associated Local Bibliographic Data record.

        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Bibliographic Data record.
                Can be an integer or string.
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a Control Number, retrieve a Local Bibliographic Data record.

        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Bibliographic Data record.
                Can be an integer or string.
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        url = self._url_manage_lbd(controlNumber)
        header = {"Accept": responseFormat}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lbd_replace(
        self,
        controlNumber: Union[int, str],
        record: str,
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a Control Number, find the associated Local Bibliographic Data
        Record and replace it. If the Control Number is not found in
        WorldCat, then the provided Local Bibliographic Data Record will be created.

        Uses /manage/lbds/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Bibliographic Data record.
                Can be an integer or string.
            record:
                MARC record to replace existing Local Bibliographic Data record.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        record: str,
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a local holdings record, create it in WorldCat

        Uses /manage/lhrs endpoint.

        Args:
            record:
                MARC holdings record to be created.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a control number, delete a Local Holdings record.

        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Holdings record.
                Can be an integer or string.
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Send a GET request for a local holdings record

        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Holdings record.
                Can be an integer or string.
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
        url = self._url_manage_lhr(controlNumber)
        header = {"Accept": responseFormat}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def lhr_replace(
        self,
        controlNumber: Union[int, str],
        record: str,
        recordFormat: str,
        responseFormat: str = "application/marcxml+xml",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a Control Number, find the associated Local Holdings
        Record and replace it. If the Control Number is not found in
        WorldCat, then the provided Local Holdings Record will be created.

        Uses /manage/lhrs/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Holdings record.
                Can be an integer or string.
            record:
                MARC holdings record to replace existing local holdings record.
            recordFormat:
                Format of MARC record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            responseFormat:
                Format of returned record.

                **OPTIONS:** `'application/marcxml+xml'` or `'application/marc'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
    ) -> Response:
        """
        Retrieve LBD Resource.

        Uses /search/my-local-bib-data/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Bibliographic Data record.
                Can be an integer or string.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        offset: int = 1,
        limit: int = 10,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Search LBD Resources using WorldCat query syntax. See OCLC
        [Local Bibliographic Data Record Index](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Local_bibliographic_data_records/Local_bibliographic_data_record_indexes_A-Z)
        Documentation for more information on available indexes.

        Uses /search/my-local-bib-data endpoint.

        Args:
            q:
                Query in the form of a keyword search or fielded search.

                **EXAMPLES:**

                - `ti:Zendegi`
                - `ti:"Czarne oceany"`
                - `bn:9781680502404`
                - `kw:python databases`
                - `ti:Zendegi AND au:greg egan`
                - `(au:Okken OR au:Myers) AND su:python`
            offset:
                Start position of bibliographic records to return.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """  # noqa: E501
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
        holdingLocation: str,
        shelvingLocation: str,
        callNumber: str,
        oclcNumber: Optional[Union[int, str]] = None,
        browsePosition: int = 0,
        limit: int = 10,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Browse local holdings.

        Uses /browse/my-holdings endpoint.

        Args:
            holdingLocation:
                Holding location for item.
            shelvingLocation:
                Shelving location for item.
            callNumber:
                Call number for item.
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            browsePosition:
                Position within browse list where the matching record should be.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
    ) -> Response:
        """
        Retrieve LHR Resource.

        Uses /search/my-holdings/{controlNumber} endpoint.

        Args:
            controlNumber:
                Control number associated with Local Holdings record.
                Can be an integer or string.
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        orderBy: str = "oclcSymbol",
        offset: int = 1,
        limit: int = 10,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Search LHR Resources. Query must contain, at minimum, either an
        `oclcNumber` or `barcode`.

        Uses /search/my-holdings endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            barcode:
                Barcode as a string.
            orderBy:
                Results sort key.

                **OPTIONS:** `'commitmentExpirationDate'`, `'location'`, `'oclcSymbol'`
            offset:
                Start position of bibliographic records to return.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
        orderBy: str = "oclcSymbol",
        offset: int = 1,
        limit: int = 10,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Search for shared print LHR Resources. Query must contain, at minimum,
        either an `oclcNumber` or `barcode` and a value for either
        `heldBySymbol`, `heldByInstitutionID` or `spProgram`.

        Uses /search/retained-holdings endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            barcode:
                Barcode as a string.
            heldBySymbol:
                Restricts to holdings with specified institution symbol.
            heldByInstitutionID:
                Restrict to specified institution registryId.
            spProgram:
                Limits response to bibliographic records associated with
                particular shared print program.
            orderBy:
                Results sort key.

                **OPTIONS:** `'commitmentExpirationDate'`, `'location'`, `'oclcSymbol'`
            offset:
                Start position of bibliographic records to return.
            limit:
                Maximum number of records to return.

                **MAXIMUM:** `50`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
    ) -> Response:
        """
        Finds member shared print holdings for specified item. Query must
        contain, at minimum, either an `oclcNumber`, `isbn`, or `issn`.

        Uses /search/bibs-retained-holdings endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            isbn:
                ISBN without any dashes.

                **EXAMPLE:** `'978149191646x'`
            issn:
                ISSN, hyphenated.

                **EXAMPLE:** `'0099-1234'`
            heldByGroup:
                Restricts to holdings held by group symbol.
            heldInState:
                Restricts to holdings held by institutions in requested state.

                **EXAMPLE:** `'US-NY'`
            itemType:
                Limits response to specified item type.

                **EXAMPLES:** `'book'`, `'vis'`
            itemSubType:
                Limits response to specified item sub type

                **EXAMPLES:** `'book-digital'`, `'audiobook-cd'`
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        preferredLanguage: str = "eng",
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
        unit: str = "M",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a known item, get summary of holdings and brief bib record. Query must
        contain, at minimum, either an OCLC Number, ISBN, or ISSN. Query may contain
        only one of: `heldByInstitutionId`, `heldByGroup`, `heldBySymbol`,
        `heldInCountry`, `heldInState` or combination of `lat`, `lon` and
        `distance`. If using lat/lon arguments, query must contain a valid
        distance argument.

        Uses /search/bibs-summary-holdings endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            isbn:
                ISBN without any dashes.

                **EXAMPLE:** `'978149191646x'`
            issn:
                ISSN, hyphenated.

                **EXAMPLE:** `'0099-1234'`
            holdingsAllEditions:
                Get holdings for all editions.

                **OPTIONS:** `True` or `False`
            holdingsAllVariantRecords:
                Get holdings for specific edition across variant records.

                **OPTIONS:** `True` or `False`
            preferredLanguage:
                Language user would prefer metadata description in. Does not limit
                responses. To limit responses use `inCataloglanguage` facet.
            holdingsFilterFormat:
                Get holdings for specific itemSubType.

                **EXAMPLE:** `'book-digital'`
            heldInCountry:
                Restricts to holdings held by institutions in requested country.
            heldInState:
                Restricts to holdings held by institutions in requested state.

                **EXAMPLE:** `'US-NY'`
            heldByGroup:
                Restricts to holdings held by group symbol.
            heldBySymbol:
                Limits to holdings held by institutions indicated by
                institution symbol.
            heldByInstitutionID:
                Limits to holdings held by institutions indicated by institution
                registryID.
            heldByLibraryType:
                Limits to holdings held by library type.

                **OPTIONS:** `'PUBLIC'`, `'ALL'`
            lat:
                Latitude

                **EXAMPLE:** `37.502508`
            lon:
                Longitude

                **EXAMPLE:** `-122.22702`
            distance:
                Limits results to holdings held by institutions within specified
                distance from latitude and longitude.
            unit:
                Unit of distance from latitude and longitude.

                **OPTIONS:** `'M'` (miles) or `'K'` (kilometers).
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
        """
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
        unit: str = "M",
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given an OCLC number, get summary of holdings. Query may contain
        only one of: `heldByInstitutionId`, `heldByGroup`, `heldBySymbol`,
        `heldInCountry`, `heldInState` or combination of `lat`, `lon` and
        `distance`. If using lat/lon arguments, query must contain a valid
        distance argument.

        Uses /search/summary-holdings endpoint.

        Args:
            oclcNumber:
                OCLC bibliographic record number. Can be an integer or string
                with or without OCLC Number prefix.
            holdingsAllEditions:
                Get holdings for all editions.

                **OPTIONS:** `True` or `False`
            holdingsAllVariantRecords:
                Get holdings for specific edition across variant records.

                **OPTIONS:** `True` or `False`
            holdingsFilterFormat:
                Get holdings for specific itemSubType.

                **EXAMPLE:** `'book-digital'`
            heldInCountry:
                Restricts to holdings held by institutions in requested country.
            heldInState:
                Restricts to holdings held by institutions in requested state.

                **EXAMPLE:** `'US-NY'`
            heldByGroup:
                Restricts to holdings held by group symbol.
            heldBySymbol:
                Limits to holdings held by institutions indicated by
                institution symbol.
            heldByInstitutionID:
                Limits to holdings held by institutions indicated by institution
                registryID.
            heldByLibraryType:
                Limits to holdings held by library type.

                **OPTIONS:** `'PUBLIC'`, `'ALL'`
            lat:
                Latitude

                **EXAMPLE:** `37.502508`
            lon:
                Longitude

                **EXAMPLE:** `-122.22702`
            distance:
                Limits results to holdings held by institutions within specified
                distance from latitude and longitude.
            unit:
                Unit of distance from latitude and longitude.

                **OPTIONS:** `'M'` (miles) or `'K'` (kilometers).
            hooks:
                Requests library hook system that can be used for signal event
                handling. For more information see the [Requests docs](https://requests.
                readthedocs.io/en/master/user/advanced/#event-hooks)

        Returns:
            `requests.Response` instance
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
