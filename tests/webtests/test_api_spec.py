# -*- coding: utf-8 -*-
import ast
import inspect
from functools import cached_property
from typing import Callable

import pytest
import requests
import yaml

from bookops_worldcat import MetadataSession


@pytest.mark.webtest
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

    def params_from_yaml(self, method: Callable) -> list:
        """
        Reads yaml file from OCLC API documentation (available here:
        https://developer.api.oclc.org/wc-metadata-v2) and returns list of
        parameters for a given endpoint. This assumes that OCLC updates this
        .yaml file with up-to-date information about the API endpoints, parameters
        and responses. This fixture does not account for endpoints that retrieve
        data related to local holdings or bib records as these are not tested
        during the monthly API tests. Function removes any deprecated params and
        the "Accept" param as it is not specific to the API.

        Reads source code of `MetadataSession` method passed to `method` arg to get
        HTTP request method and endpoint used in API call made by the method.

        Args:
            method: method within `MetadataSession` class

        Returns:
            a list of parameters for the endpoint as defined in the API spec
        """
        http_req_method = ""
        url_source = ""
        for node in ast.walk(ast.parse(inspect.getsource(method).lstrip("    "))):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                args = node.value.args
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "Request":
                    http_req_method = [i.value for i in args if hasattr(i, "value")][0]
                elif isinstance(func, ast.Attribute) and func.attr.startswith("_"):
                    url_source = inspect.getsource(getattr(MetadataSession, func.attr))

        endpoint = ""
        for node in ast.walk(ast.parse(url_source.lstrip("    "))):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.JoinedStr):
                values = [i.value for i in node.value.values if hasattr(i, "value")]
                endpoint_parts = [i for i in values if isinstance(i, (ast.Name, str))]
                out = []
                for part in endpoint_parts:
                    out_part = f"{{{part.id}}}" if isinstance(part, ast.Name) else part
                    out.append(out_part)
                endpoint = "/worldcat" + "".join(out)
        params = self.endpoints[endpoint][http_req_method.lower()].get("parameters")
        if not params:
            return []
        if any("name" not in i.keys() for i in params):
            lookup = self.api_spec_dict["components"]["parameters"]
            refs = [i["$ref"].split("/")[-1] for i in params]
            params = [lookup[i] for i in refs if "deprecated" not in lookup[i]]
        return [i["name"] for i in params if i["name"] != "Accept"]

    def params_from_method(self, method: Callable) -> list:
        """
        Inspects signature of `MetadataSession` method and and returns list
        of parameters to compare to parameters included in OpenAPI spec. Filters
        "responseFormat", "hooks", "self", and "Accept" parameters as they are specific
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
            if i
            not in [
                "Accept",
                "hooks",
                "record",
                "responseFormat",
                "recordFormat",
                "self",
            ]
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
                "/worldcat/manage/institution/holdings/move",
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
                "/worldcat/search/institution",
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
                "/worldcat/search/institution",
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
                "/worldcat/manage/institution/holdings/move",
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

    def test_params_bib_get(self):
        endpoint_args = self.params_from_yaml(MetadataSession.bib_get)
        method_args = self.params_from_method(MetadataSession.bib_get)
        assert endpoint_args == method_args

    def test_params_bib_get_classification(self):
        endpoint_args = self.params_from_yaml(MetadataSession.bib_get_classification)
        method_args = self.params_from_method(MetadataSession.bib_get_classification)
        assert endpoint_args == method_args

    def test_params_bib_get_current_oclc_number(self):
        endpoint_args = self.params_from_yaml(
            MetadataSession.bib_get_current_oclc_number
        )
        method_args = self.params_from_method(
            MetadataSession.bib_get_current_oclc_number
        )
        assert endpoint_args == method_args

    def test_params_bib_match(self):
        endpoint_args = self.params_from_yaml(MetadataSession.bib_match)
        method_args = self.params_from_method(MetadataSession.bib_match)
        assert endpoint_args == method_args

    def test_params_bib_validate(self):
        endpoint_args = self.params_from_yaml(MetadataSession.bib_validate)
        method_args = self.params_from_method(MetadataSession.bib_validate)
        assert endpoint_args == method_args

    def test_params_branch_holding_codes_get(self):
        endpoint_args = self.params_from_yaml(MetadataSession.branch_holding_codes_get)
        method_args = self.params_from_method(MetadataSession.branch_holding_codes_get)
        assert endpoint_args == method_args

    def test_params_brief_bibs_get(self):
        endpoint_args = self.params_from_yaml(MetadataSession.brief_bibs_get)
        method_args = self.params_from_method(MetadataSession.brief_bibs_get)
        assert endpoint_args == method_args

    def test_params_brief_bibs_search(self):
        endpoint_args = self.params_from_yaml(MetadataSession.brief_bibs_search)
        method_args = self.params_from_method(MetadataSession.brief_bibs_search)
        assert endpoint_args == method_args

    def test_params_brief_bibs_get_other_editions(self):
        endpoint_args = self.params_from_yaml(
            MetadataSession.brief_bibs_get_other_editions
        )
        method_args = self.params_from_method(
            MetadataSession.brief_bibs_get_other_editions
        )
        assert endpoint_args == method_args

    def test_params_holdings_get_codes(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_get_codes)
        method_args = self.params_from_method(MetadataSession.holdings_get_codes)
        assert endpoint_args == method_args

    def test_params_holdings_get_current(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_get_current)
        method_args = self.params_from_method(MetadataSession.holdings_get_current)
        assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_set(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_set)
        method_args = self.params_from_method(MetadataSession.holdings_set)
        assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_unset(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_unset)
        method_args = self.params_from_method(MetadataSession.holdings_unset)
        assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_set_with_bib(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_set_with_bib)
        method_args = self.params_from_method(MetadataSession.holdings_set_with_bib)
        assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_unset_with_bib(self):
        endpoint_args = self.params_from_yaml(MetadataSession.holdings_unset_with_bib)
        method_args = self.params_from_method(MetadataSession.holdings_unset_with_bib)
        assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_institution_identifiers_get(self):
        endpoint_args = self.params_from_yaml(
            MetadataSession.institution_identifiers_get
        )
        method_args = self.params_from_method(
            MetadataSession.institution_identifiers_get
        )
        assert endpoint_args == method_args

    def test_params_shared_print_holdings_search(self):
        endpoint_args = self.params_from_yaml(
            MetadataSession.shared_print_holdings_search
        )
        method_args = self.params_from_method(
            MetadataSession.shared_print_holdings_search
        )
        assert endpoint_args == method_args

    def test_params_summary_holdings_get(self):
        endpoint_args = self.params_from_yaml(MetadataSession.summary_holdings_get)
        method_args = self.params_from_method(MetadataSession.summary_holdings_get)
        assert endpoint_args == method_args

    def test_params_summary_holdings_search_oclc(self):
        endpoint_args = self.params_from_yaml(MetadataSession.summary_holdings_search)
        method_args = self.params_from_method(MetadataSession.summary_holdings_search)
        assert endpoint_args == method_args
