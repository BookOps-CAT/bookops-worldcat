# -*- coding: utf-8 -*-
from collections.abc import Callable
import inspect
import json
import os
from typing import Generator
import yaml
import pytest
import requests

from bookops_worldcat import WorldcatAccessToken


@pytest.fixture
def live_keys() -> None:
    if not os.getenv("GITHUB_ACTIONS"):
        fh = os.path.expanduser("~/.oclc/nyp_wc_test.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["WCKey"] = data["key"]
            os.environ["WCSecret"] = data["secret"]
            os.environ["WCScopes"] = data["scopes"]


@pytest.fixture(scope="class")
@pytest.mark.usefixtures("live_keys")
def live_token() -> Generator[WorldcatAccessToken, None, None]:
    """
    Gets live token from environment variables. For use with live tests so that
    the service does not need to request a new token for each test.
    """
    yield WorldcatAccessToken(
        key=os.environ["WCKey"],
        secret=os.environ["WCSecret"],
        scopes=os.environ["WCScopes"],
    )


@pytest.fixture
def method_params() -> Callable:
    """
    Inspects signature of `MetadataSession` method and and returns list
    of parameters. Filters "responseFormat", "hooks", and "Accept" parameters
    as they are specific to bookops-worldcat or the `requests` library and
    not part of the OCLC API. Filters "record" and "recordFormat" parameters as
    they are passed to the API in the request body and not as query parameters.
    """

    def get_params(method):
        all_params = list(inspect.signature(method).parameters.keys())
        return [
            i
            for i in all_params
            if i not in ["responseFormat", "hooks", "Accept", "record", "recordFormat"]
        ]

    return get_params


@pytest.fixture(scope="module")
def metadata_api_endpoints(metadata_session_open_api_spec) -> dict:
    """Retrieves endpoints from Metadata API Open API spec"""
    return metadata_session_open_api_spec["paths"]


@pytest.fixture(scope="module")
def metadata_session_open_api_spec() -> dict:
    """Retrieves OpenAPI spec from Metadata API documentation"""
    yaml_response = requests.get(
        "https://developer.api.oclc.org/docs/wc-metadata/openapi-external-prod.yaml"
    )
    return yaml.safe_load(yaml_response.text)


@pytest.fixture
def endpoint_params(metadata_session_open_api_spec) -> Callable:
    """
    Reads yaml file from OCLC API documentation (available here:
    https://developer.api.oclc.org/wc-metadata-v2) and returns list of
    parameters for a given endpoint. This assumes that OCLC updates this
    .yaml file with up-to-date information about the API endpoints, parameters
    and responses. This fixture does not account for endpoints that retrieve
    data related to local holdings or bib records as these are not tested
    during the monthly API tests. Function removes "Accept" param as it is not
    part of the API and "heldBy" as it is deprecated.
    """

    def get_params_from_yaml(url: str, method: str) -> list:
        data = metadata_session_open_api_spec
        split_url = url.split("https://metadata.api.oclc.org")[1].split("?")[0]
        if "bibs/validate/" in split_url:
            endpoint = "/worldcat/manage/bibs/validate/{validationLevel}"
        elif all(i.isdigit() is False for i in split_url):
            endpoint = split_url
        elif "institution" in split_url:
            base = "/worldcat/manage/institution/holdings/{oclcNumber}"
            endpoint = f"{base}/{split_url.split('/')[-1]}"
        elif "other-editions" in split_url:
            endpoint = "/worldcat/search/brief-bibs/{oclcNumber}/other-editions"
        elif "manage/bibs" in split_url:
            endpoint = "/worldcat/manage/bibs/{oclcNumber}"
        elif "search" in split_url and "bibs" in split_url:
            endpoint = f"{split_url.rsplit('/', 1)[0]}/{{oclcNumber}}"
        else:
            endpoint = split_url
        method = method.lower()
        if "parameters" in data["paths"][endpoint][method]:
            param_list = [i for i in data["paths"][endpoint][method]["parameters"]]
            if any("$ref" in i.keys() for i in param_list):
                params = [
                    data["components"]["parameters"][i["$ref"].split("/")[-1]]["name"]
                    for i in param_list
                ]
            elif any("name" in i.keys() for i in param_list):
                params = [
                    i["name"] for i in data["paths"][endpoint][method]["parameters"]
                ]
            else:
                params = param_list
        else:
            params = []
        return [i for i in params if i != "Accept" and i != "heldBy"]

    return get_params_from_yaml
