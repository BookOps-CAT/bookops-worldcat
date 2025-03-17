# -*- coding: utf-8 -*-
import inspect
import re
from functools import cached_property
from typing import Callable, List

import pytest
import requests
import yaml

from bookops_worldcat import MetadataSession


@pytest.mark.webtest
@pytest.mark.usefixtures("live_keys")
class TestAPISpec:
    """Compares API spec with MetadataSession methods"""

    @cached_property
    def api_spec_dict(self) -> dict:
        """
        Retrieves OpenAPI spec from Metadata API documentation. Caches response
        so it can be reused in multiple tests without additional API requests.
        Returns API spec as a dictionary.
        """
        yaml_response = requests.get(
            "https://developer.api.oclc.org/docs/wc-metadata/openapi-external-prod.yaml"
        )
        return yaml.safe_load(yaml_response.text)

    @cached_property
    def endpoints(self) -> dict:
        """Retrieves endpoints from Metadata API Open API spec"""
        return self.api_spec_dict["paths"]

    def endpoint_params(self, url: str, method: str) -> List[str]:
        """
        Reads yaml file from OCLC API documentation (available here:
        https://developer.api.oclc.org/wc-metadata-v2) and returns list of
        parameters for a given endpoint. This assumes that OCLC updates this
        .yaml file with up-to-date information about the API endpoints, parameters
        and responses. This fixture does not account for endpoints that retrieve
        data related to local holdings or bib records as these are not tested
        during the monthly API tests. Function removes "Accept" param as it is not
        part of the API and any deprecated params.

        Takes url and method from `requests.Request` object and returns list of parameters
        as listed in the OCLC Metadata API documentation.

        Args:
            url: a url as a string (from `url` attribute of `requests.Request` object)
            method: an http method as a string

        Returns:
            a list of parameters for the endpoint as defined in the API spec
        """
        url = url.split("https://metadata.api.oclc.org")[1].split("?")[0]
        pattern = r"\d+"
        if "validate" in url:
            endpoint = f"{url.rsplit('/', 1)[0]}/{{validationLevel}}"
        elif any(i in ["lbds", "lhrs", "my-"] for i in url):
            endpoint = re.sub(pattern, "{controlNumber}", url)
        else:
            endpoint = re.sub(pattern, "{oclcNumber}", url)
        params = self.endpoints[endpoint][method.lower()].get("parameters")
        if not params:
            return []
        if any("name" not in i.keys() for i in params):
            lookup = self.api_spec_dict["components"]["parameters"]
            refs = [i["$ref"].split("/")[-1] for i in params]
            params = [lookup[i] for i in refs if "deprecated" not in lookup[i]]
        return [i["name"] for i in params if i["name"] != "Accept"]

    def method_params(self, method: Callable) -> list:
        """
        Inspects signature of `MetadataSession` method and and returns list
        of parameters to compare to parameters included in OpenAPI spec. Filters
        "responseFormat", "hooks", and "Accept" parameters as they are specific
        to bookops-worldcat or the `requests` library and not part of the OCLC API.
        Filters "record" and "recordFormat" parameters as they are passed to the API
        in the request body and not as query parameters.

        Args:
            method: method within `MetadataSession` class

        Returns:
            list of parameters available to `MetadataSession` method
        """
        return [
            i
            for i in list(inspect.signature(method).parameters.keys())
            if i not in ["Accept", "hooks", "record", "responseFormat", "recordFormat"]
        ]

    def test_check_endpoint_list(self):
        """Confirm API spec contains the same endpoints as expected."""
        assert sorted(self.endpoints) == sorted(
            [
                "/worldcat/manage/bibs/validate/{validationLevel}",
                "/worldcat/manage/bibs/current",
                "/worldcat/manage/bibs",
                "/worldcat/manage/bibs/{oclcNumber}",
                "/worldcat/manage/bibs/match",
                "/worldcat/manage/institution/holdings/current",
                "/worldcat/manage/institution/holdings/{oclcNumber}/set",
                "/worldcat/manage/institution/holdings/{oclcNumber}/unset",
                "/worldcat/manage/institution/holdings/set",
                "/worldcat/manage/institution/holdings/unset",
                "/worldcat/manage/institution/holding-codes",
                "/worldcat/manage/institution-config/branch-shelving-locations",
                "/worldcat/manage/lbds/{controlNumber}",
                "/worldcat/manage/lbds",
                "/worldcat/manage/lhrs/{controlNumber}",
                "/worldcat/manage/lhrs",
                "/worldcat/search/brief-bibs",
                "/worldcat/search/brief-bibs/{oclcNumber}",
                "/worldcat/search/classification-bibs/{oclcNumber}",
                "/worldcat/search/brief-bibs/{oclcNumber}/other-editions",
                "/worldcat/search/bibs-retained-holdings",
                "/worldcat/search/bibs-summary-holdings",
                "/worldcat/search/bibs/{oclcNumber}",
                "/worldcat/search/summary-holdings",
                "/worldcat/search/retained-holdings",
                "/worldcat/search/my-local-bib-data/{controlNumber}",
                "/worldcat/search/my-local-bib-data",
                "/worldcat/search/my-holdings/{controlNumber}",
                "/worldcat/search/my-holdings",
                "/worldcat/browse/my-holdings",
            ]
        )

    def test_check_endpoint_methods_delete(self):
        """Confirm expected endpoints allow for DELETE method."""
        delete_endpoints = [
            i for i in self.endpoints if "delete" in list(self.endpoints[i].keys())
        ]
        assert sorted(delete_endpoints) == sorted(
            [
                "/worldcat/manage/lbds/{controlNumber}",
                "/worldcat/manage/lhrs/{controlNumber}",
            ]
        )

    def test_check_endpoint_methods_get(self):
        """Confirm expected endpoints allow for GET method."""
        get_endpoints = [
            i for i in self.endpoints if "get" in list(self.endpoints[i].keys())
        ]
        assert sorted(get_endpoints) == sorted(
            [
                "/worldcat/manage/bibs/{oclcNumber}",
                "/worldcat/manage/bibs/current",
                "/worldcat/manage/institution/holdings/current",
                "/worldcat/manage/institution/holding-codes",
                "/worldcat/manage/institution-config/branch-shelving-locations",
                "/worldcat/manage/lbds/{controlNumber}",
                "/worldcat/manage/lhrs/{controlNumber}",
                "/worldcat/search/brief-bibs",
                "/worldcat/search/brief-bibs/{oclcNumber}",
                "/worldcat/search/classification-bibs/{oclcNumber}",
                "/worldcat/search/brief-bibs/{oclcNumber}/other-editions",
                "/worldcat/search/bibs-retained-holdings",
                "/worldcat/search/bibs-summary-holdings",
                "/worldcat/search/bibs/{oclcNumber}",
                "/worldcat/search/summary-holdings",
                "/worldcat/search/retained-holdings",
                "/worldcat/search/my-local-bib-data/{controlNumber}",
                "/worldcat/search/my-local-bib-data",
                "/worldcat/search/my-holdings/{controlNumber}",
                "/worldcat/search/my-holdings",
                "/worldcat/browse/my-holdings",
            ]
        )

    def test_check_endpoint_methods_post(self):
        """Confirm expected endpoints allow for POST method."""
        post_endpoints = [
            i for i in self.endpoints if "post" in list(self.endpoints[i].keys())
        ]
        assert sorted(post_endpoints) == sorted(
            [
                "/worldcat/manage/bibs/validate/{validationLevel}",
                "/worldcat/manage/bibs",
                "/worldcat/manage/bibs/match",
                "/worldcat/manage/institution/holdings/{oclcNumber}/set",
                "/worldcat/manage/institution/holdings/{oclcNumber}/unset",
                "/worldcat/manage/institution/holdings/set",
                "/worldcat/manage/institution/holdings/unset",
                "/worldcat/manage/lbds",
                "/worldcat/manage/lhrs",
            ]
        )

    def test_check_endpoint_methods_put(self):
        """Confirm expected endpoints allow for PUT method."""
        put_endpoints = [
            i for i in self.endpoints if "put" in list(self.endpoints[i].keys())
        ]
        assert sorted(put_endpoints) == sorted(
            [
                "/worldcat/manage/bibs/{oclcNumber}",
                "/worldcat/manage/lbds/{controlNumber}",
                "/worldcat/manage/lhrs/{controlNumber}",
            ]
        )

    def test_params_bib_get(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.bib_get(41266045)
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.bib_get)
            assert endpoint_args == method_args

    def test_params_bib_get_classification(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.bib_get_classification(41266045)
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.bib_get_classification)
            assert endpoint_args == method_args

    def test_params_bib_get_current_oclc_number(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.bib_get_current_oclc_number([41266045, 519740398])
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.bib_get_current_oclc_number)
            assert endpoint_args == method_args

    def test_params_bib_match_marcxml(self, live_token, stub_marc_xml):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.bib_match(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.bib_match)
            assert endpoint_args == method_args

    def test_params_bib_validate(self, live_token, stub_marc21):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.bib_validate(
                stub_marc21, recordFormat="application/marc"
            )
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.bib_validate)
            assert endpoint_args == method_args

    def test_params_brief_bibs_get(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.brief_bibs_get(41266045)
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.brief_bibs_get)
            assert endpoint_args == method_args

    def test_params_brief_bibs_search(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.brief_bibs_search(
                q="ti:Zendegi", inLanguage="eng", inCatalogLanguage="eng"
            )
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.brief_bibs_search)
            assert endpoint_args == method_args

    def test_params_brief_bibs_get_other_editions(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.brief_bibs_get_other_editions(41266045)
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.brief_bibs_get_other_editions)
            assert endpoint_args == method_args

    def test_params_holdings_get_codes(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.holdings_get_codes()
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.holdings_get_codes)
            assert endpoint_args == method_args

    def test_params_holdings_get_current(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.holdings_get_current("982651100")
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.holdings_get_current)
            assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_set_unset(self, live_token):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
            get_response = session.holdings_get_current("850940548")
            holdings = get_response.json()["holdings"]
            current_holding_endpoint_args = self.endpoint_params(
                get_response.request.url, get_response.request.method
            )
            current_holding_method_args = self.method_params(
                session.holdings_get_current
            )
            assert current_holding_endpoint_args == current_holding_method_args

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset(850940548)

            # test setting holdings
            set_response = session.holdings_set(850940548)
            set_holding_endpoint_args = self.endpoint_params(
                set_response.request.url, set_response.request.method
            )
            set_holding_method_args = self.method_params(session.holdings_set)
            assert set_holding_endpoint_args == set_holding_method_args

            # test deleting holdings
            unset_response = session.holdings_unset(oclcNumber=850940548)
            unset_holding_endpoint_args = self.endpoint_params(
                unset_response.request.url, unset_response.request.method
            )
            unset_holding_method_args = self.method_params(session.holdings_unset)
            assert unset_holding_endpoint_args == unset_holding_method_args

    @pytest.mark.holdings
    def test_params_holdings_set_unset_with_bib(self, live_token, stub_marc_xml):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
            get_response = session.holdings_get_current("850940548")
            holdings = get_response.json()["holdings"]
            current_holding_endpoint_args = self.endpoint_params(
                get_response.request.url, get_response.request.method
            )
            current_holding_method_args = self.method_params(
                session.holdings_get_current
            )
            assert current_holding_endpoint_args == current_holding_method_args

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset_with_bib(
                    stub_marc_xml, recordFormat="application/marcxml+xml"
                )

            # test setting holdings
            set_response = session.holdings_set_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            set_holding_endpoint_args = self.endpoint_params(
                set_response.request.url, set_response.request.method
            )
            set_holding_method_args = self.method_params(session.holdings_set_with_bib)
            assert set_holding_endpoint_args == set_holding_method_args

            # test deleting holdings
            unset_response = session.holdings_unset_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            unset_holding_endpoint_args = self.endpoint_params(
                unset_response.request.url, unset_response.request.method
            )
            unset_holding_method_args = self.method_params(
                session.holdings_unset_with_bib
            )
            assert unset_holding_endpoint_args == unset_holding_method_args

    def test_params_shared_print_holdings_search(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.shared_print_holdings_search(oclcNumber="41266045")
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.shared_print_holdings_search)
            assert endpoint_args == method_args

    def test_params_summary_holdings_get(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.summary_holdings_get("41266045")
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.summary_holdings_get)
            assert endpoint_args == method_args

    def test_params_summary_holdings_search_oclc(self, live_token):
        with MetadataSession(authorization=live_token, totalRetries=2) as session:
            response = session.summary_holdings_search(oclcNumber="41266045")
            endpoint_args = self.endpoint_params(
                response.request.url, response.request.method
            )
            method_args = self.method_params(session.summary_holdings_search)
            assert endpoint_args == method_args
