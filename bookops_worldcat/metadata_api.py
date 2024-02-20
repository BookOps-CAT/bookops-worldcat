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
        return "https://metadata.api.oclc.org/worldcat"

    def _url_manage_bib_validate(self, validationLevel: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/bibs/validate/{validationLevel}"

    def _url_manage_bib_current_oclc_number(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/bibs/current"

    def _url_manage_bib_create(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/bibs"

    def _url_manage_bib(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/bibs/{oclcNumber}"

    def _url_manage_bib_match(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/bibs/match"

    def _url_manage_ih_current(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holdings/current"

    def _url_manage_ih_set(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holdings/set"

    def _url_manage_ih_unset(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holdings/unset"

    def _url_manage_ih_oclc_number_set(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holdings/{oclcNumber}/set"

    def _url_manage_ih_oclc_number_unset(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holdings/{oclcNumber}/unset"

    def _url_manage_ih_codes(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/institution/holding-codes"

    def _url_manage_lbd_create(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/lbds"

    def _url_manage_lbd(self, controlNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/lbds/{controlNumber}"

    def _url_manage_lhr_create(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/lhrs"

    def _url_manage_lhr(self, controlNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/manage/lhrs/{controlNumber}"

    def _url_search_shared_print_holdings(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/bibs-retained-holdings"

    def _url_search_general_holdings(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/bibs-summary-holdings"

    def _url_search_general_holdings_summary(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/summary-holdings"

    def _url_search_brief_bibs(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/brief-bibs"

    def _url_search_brief_bibs_oclc_number(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/brief-bibs/{oclcNumber}"

    def _url_search_brief_bibs_other_editions(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/brief-bibs/{oclcNumber}/other-editions"

    def _url_search_classification_bibs(self, oclcNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/classification-bibs/{oclcNumber}"

    def _url_search_lhr_shared_print(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/retained-holdings"

    def _url_search_lhr_control_number(self, controlNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/my-holdings/{controlNumber}"

    def _url_search_lhr(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/my-holdings"

    def _url_browse_lhr(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/browse/my-holdings"

    def _url_search_lbd_control_number(self, controlNumber: str) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/my-local-bib-data/{controlNumber}"

    def _url_search_lbd(self) -> str:
        base_url = self._url_base()
        return f"{base_url}/search/my-local-bib-data"

    # Manage Bibliographic Resources

    def validate_bib(
        self,
        validationLevel: Optional[str],
        record: str,
        recordFormat: Optional[str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Response:
        """
        Given a bib record, validate that record conforms to MARC standards
        Uses /manage/bibs/validate/{validationLevel} endpoint.

        Args:
            validationLevel:        Level at which to validate records
                                    available values: validateFull, validateAdd,
                                    validateReplace
                                    default is validateFull
            record:                 MARC record to be validated
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """

        # check if validationLevel arg is valid
        if validationLevel and validationLevel not in [
            "validateFull",
            "validateAdd",
            "validateReplace",
        ]:
            raise TypeError("Invalid validationLevel was passed as an argument")

        # defaults to validateFull if validationLevel is not provided
        if not validationLevel:
            validationLevel = "validateFull"

        # defaults to marcxml if recordFormat is not provided
        if not recordFormat:
            recordFormat = "application/marcxml+xml"

        url = self._url_manage_bib_validate(validationLevel)
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def search_current_control_numbers(
        self,
        oclcNumbers: Union[str, List[Union[str, int]]],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve current OCLC control numbers
        Uses /manage/bibs/current endpoint.

        Args:
            oclcNumbers:            list of OCLC control numbers to be checked;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
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

    def create_bib(
        self,
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Create a bib record in OCLC if it does not already exist
        Uses /manage/bibs/ endpoint.

        Args:
            record:                 MARC record to be validated
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """

        if recordFormat and recordFormat not in [
            "application/marc",
            "application/marcxml+xml",
        ]:
            raise TypeError("Invalid recordFormat was passed as an argument")

        url = self._url_manage_bib_create()
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
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
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
                                    if str the numbers must be separated by comma
            responseFormat:         format of returned record, accepts MARC21 or MARCXML
                                    defaul is MARCXML
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        # defaults to marcxml if responseFormat is not provided
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

    def replace_bib(
        self,
        oclcNumber: Union[int, str],
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC number, replace the bib record
        If the bib record does not exist, then a new bib record will be created
        Uses /manage/bibs/{oclcNumber} endpoint.

        Args:
            oclcNumber:             OCLC bibliographic record number; can be an
                                    integer, or string with or without OCLC # prefix
            record:                 new record to replace old record
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        oclcNumber = verify_oclc_number(oclcNumber)

        if recordFormat and recordFormat not in [
            "application/marc",
            "application/marcxml+xml",
        ]:
            raise TypeError("Invalid recordFormat was passed as an argument")

        url = self._url_manage_bib(oclcNumber)
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("PUT", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def match_bib(
        self,
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given a bib record in MARC21 or MARCXML identify the best match
        Uses /manage/bibs/match endpoint.

        Args:
            record:                 MARC record to be matched
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` instance
        """
        # work in progress
        # takes MARC XML or MARC21 as request body

        if recordFormat and recordFormat not in [
            "application/marc",
            "application/marcxml+xml",
        ]:
            raise TypeError("Invalid recordFormat was passed as an argument")

        url = self._url_manage_bib_match()
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    # Manage Institution

    def holding_get_status(
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
            oclcNumbers:            list of OCLC control numbers to be checked;
                                    they can be integers or strings with or
                                    without OCLC # prefix;
                                    if str the numbers must be separated by comma
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

    def bib_holding_set(
        self,
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Set holdings on a bib record
        Uses /manage/institution/holdings/set/ endpoint.

        Args:
            record:                 MARC record on which to set holdings
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if recordFormat and recordFormat not in [
            "application/marc",
            "application/marcxml+xml",
        ]:
            raise TypeError("Invalid recordFormat was passed as an argument")

        url = self._url_manage_ih_set()
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def bib_holding_unset(
        self,
        record: str,
        recordFormat: str,
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Unset holdings on a bib record
        Uses /manage/institution/holdings/unset/ endpoint.

        Args:
            record:                 MARC record on which to unset holdings
            recordFormat:           format for MARC record, options:
                                    "application/marc", "application/marcxml+xml"
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks
        Returns:
            `requests.Response` object
        """
        if recordFormat and recordFormat not in [
            "application/marc",
            "application/marcxml+xml",
        ]:
            raise TypeError("Invalid recordFormat was passed as an argument")

        url = self._url_manage_ih_unset()
        header = {"Accept": "application/json", "content-type": recordFormat}

        # prep request
        req = Request("POST", url, data=record, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def holding_set(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Given an OCLC Number, set holdings on a bib record
        Uses /manage/institution/holdings/{oclcNumber}/set/ endpoint.

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

        url = self._url_manage_ih_oclc_number_set(oclcNumber)
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
        Given an OCLC Number, unset holdings on a bib record
        Uses /manage/institution/holdings/{oclcNumber}/unset/ endpoint.

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

        url = self._url_manage_ih_oclc_number_unset(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("POST", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def get_holding_codes(
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

    # Manage Local Bibliographic Data
    # def manage_lbd_create():

    # def manage_lbd_get():

    # def manage_lbd_replace():

    # def manage_lbd_delete():

    # # Manage Local Holdings Records

    # def manage_lhrs_create():

    # def manage_lhrs_get():

    # def manage_lhrs_replace():

    # def manage_lhrs_delete():

    # Search Member Shared Print Holdings
    def search_shared_print_holdings(
        self,
        oclcNumber: Union[int, str],
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
                                    example: "978149191646x"
            issn:                   ISSN with hyphen, example: "0099-1234"
            heldByGroup:            limits to holdings held by institutions
                                    indicated by group symbol
            heldInState:            limits to holdings held by institutions in
                                    requested state, example: "US-NY"
            itemType:               limits results to specified item type
                                    examples: "book" or "vis"
            itemSubType:            limits results to specified item sub type
                                    examples: "book-digital" or "audiobook-cd"
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

    # Search Member General Holdings
    def search_general_holdings(
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
        Given a known item get summary of holdings and brief bib record
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
            heldInCountry:              limits to holdings held by institutions
                                        in requested country
            heldInState:                limits to holdings held by institutions
                                        in requested state, example: "US-NY"
            heldByGroup:                limits to holdings held by institutions
                                        indicated by group symbol
            heldBySymbol:               limits to holdings held by institutions
                                        indicated by institution symbol
            heldByInstitutionID:        limits to holdings held by institutions
                                        indicated by institution registryID
            heldByLibraryType:          limits to holdings held by library type,
                                        options: "PUBLIC", "ALL"
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

    def search_general_holdings_summary(
        self,
        oclcNumber: Union[int, str],
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
        Given an OCLC number get summary of holdings
        Uses /search/summary-holdings/ endpoint.

        Args:
            oclcNumber:                 OCLC bibliographic record number; can be
                                        an integer, or string that can include
                                        OCLC # prefix
            holdingsAllEditions:        get holdings for all editions;
                                        options: True, False
            holdingsAllVariantRecords:  get holdings for specific edition across variant
                                        records; options: True, False
            preferredLanguage:          language of metadata description;
                                        default 'en' (English)
            holdingsFilterFormat:       get holdings for specific itemSubType,
                                        example: book-digital
            heldInCountry:              limits to holdings held by institutions
                                        in requested country
            heldInState:                limits to holdings held by institutions
                                        in requested state, example: "US-NY"
            heldByGroup:                limits to holdings held by institutions
                                        indicated by group symbol
            heldBySymbol:               limits to holdings held by institutions
                                        indicated by institution symbol
            heldByInstitutionID:        limits to holdings held by institutions
                                        indicated by institution registryID
            heldByLibraryType:          limits to holdings held by library type,
                                        options: "PUBLIC", "ALL"
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

    # Search Bibliographic Resources
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
                                    for multiple values repeat the parameter,
                                    example:
                                        '794,180'
            datePublished:          restricts the response to one or
                                    more dates, or to a range,
                                    examples:
                                        '2000'
                                        '2000-2005'
                                        '2000,2005'
            heldByGroup:            limits to holdings held by institutions
                                    indicated by group symbol
            heldBySymbol:           limits to holdings held by institutions
                                    indicated by institution symbol
            heldByInstitutionID:    limits to holdings held by institutions
                                    indicated by institution registryID
            inLanguage:             restricts the response to the single
                                    specified language, example: 'fre'
            inCataloglanguage:      restricts the response to specified
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
                                    available values: "juv", "nonJuv"
            content:                content to limit results to,
                                    avaiable values: "fic", "nonFic", "bio"
            openAccess:             limit to just open access content
            peerReviewed:           limit to just peer reviewed content
            facets:                 list of facets to restrict responses
                                    available values: 'subject', 'creator',
                                    'datePublished', 'genre', 'itemType',
                                    'itemSubTypeBrief', 'itemSubType', 'language',
                                    'topic', 'subtopic', 'content', 'audience',
                                    'databases'
            groupRelatedEditions:   whether or not use FRBR grouping,
                                    options: False, True (default is False)
            groupVariantRecords:    whether or not to group variant records.
                                    options: False, True (default False)
            preferredLanguage:      language of metadata description,
                                    default is "en" (English)
            showHoldingsIndicators: whether or not to show holdings indicators in
                                    response. options: False, True (default is False)
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

    def search_brief_bib_other_editions(
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
            genre:                  genre to limit results to (ge index)
            topic:                  topic to limit results to (s0 index)
            subtopic:               subtopic to limit results to (s1 index)
            audience:               audience to limit results to,
                                    available values: "juv", "nonJuv"
            content:                content to limit results to
                                    avaiable values: "fic", "nonFic", "bio"
            openAccess:             limit to just open access content
            peerReviewed:           limit to just peer reviewed content
            facets:                 list of facets to restrict responses
                                    available values: 'subject', 'creator',
                                    'datePublished', 'genre', 'itemType',
                                    'itemSubTypeBrief', 'itemSubType', 'language',
                                    'topic', 'subtopic', 'content', 'audience',
                                    'databases'
            groupRelatedEditions:   whether or not use FRBR grouping,
                                    options: False, True (default is False)
            groupVariantRecords:    whether or not to group variant records.
                                    options: False, True (default False)
            preferredLanguage:      language of metadata description,
                                    default is "en" (English)
            showHoldingsIndicators: whether or not to show holdings indicators in
                                    response. options: False, True (default is False)
            offset:                 start position of bibliographic records to
                                    return; default 1
            limit:                  maximum nuber of records to return;
                                    maximum 50, default 10
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

    def get_bib_classification(
        self,
        oclcNumber: Union[int, str],
        hooks: Optional[Dict[str, Callable]] = None,
    ) -> Optional[Response]:
        """
        Retrieve classification recommendations for an OCLC number.
        Uses /search/classification-bibs/{oclcNumber}/other-editions endpoint.

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

        url = self._url_search_classification_bibs(oclcNumber)
        header = {"Accept": "application/json"}

        # prep request
        req = Request("GET", url, headers=header, hooks=hooks)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    # Search Local Holdings Resources
    # def search_lhr_shared_print():

    # def search_lhr_control_number():

    # def search_lhr():

    # def browse_lhr():

    # Search Local Bib Resources
    # def search_lbd_control_number():

    # def search_lbd():
