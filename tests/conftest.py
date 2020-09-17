# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import os

import pytest
import requests


from bookops_worldcat import WorldcatAccessToken
from bookops_worldcat.errors import WorldcatAuthorizationError


class MockAuthServerResponseSuccess:
    """Simulates auth server response to successful token request"""

    def __init__(self):
        self.status_code = 200

    def json(self):
        expires_at = datetime.strftime(
            datetime.utcnow() + timedelta(0, 1199), "%Y-%m-%d %H:%M:%SZ"
        )

        return {
            "access_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
            "token_type": "bearer",
            "expires_in": "1199",
            "principalID": "",
            "principalIDNS": "",
            "scopes": "scope1",
            "contextInstitutionId": "00001",
            "expires_at": expires_at,
        }


class MockAuthServerResponseFailure:
    """Simulates auth server response to successful token request"""

    def __init__(self):
        self.status_code = 403

    def json(self):
        return {
            "code": 403,
            "message": "Invalid scope(s): invalid (invalid) [Invalid service specified, Not on key]",
        }


class MockServiceErrorResponse:
    """Simulates web service error responses"""

    def __init__(self, code, json_response, url):
        self.status_code = code
        self.msg = json_response
        self.url = url

    def json(self):
        return self.msg


class MockUnexpectedException:
    def __init__(self, *args, **kwargs):
        raise Exception


class MockTimeout:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.Timeout


class MockConnectionError:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.ConnectionError


class MockSuccessfulSessionResponse:
    def __init__(self):
        self.status_code = 200


@pytest.fixture
def mock_credentials():
    return {
        "key": "my_WSkey",
        "secret": "my_WSsecret",
        "scopes": ["scope1", "scope2"],
    }


@pytest.fixture
def mock_oauth_server_response(*args, **kwargs):
    return MockAuthServerResponseSuccess()


@pytest.fixture
def mock_successful_post_token_response(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseSuccess()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_failed_post_token_response(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseFailure()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_unexpected_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockUnexpectedException)
    monkeypatch.setattr("requests.get", MockUnexpectedException)
    monkeypatch.setattr("requests.Session.get", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.post", MockTimeout)
    monkeypatch.setattr("requests.get", MockTimeout)
    monkeypatch.setattr("requests.Session.get", MockTimeout)


@pytest.fixture
def mock_connectionerror(monkeypatch):
    monkeypatch.setattr("requests.post", MockConnectionError)
    monkeypatch.setattr("requests.get", MockConnectionError)
    monkeypatch.setattr("requests.Session.get", MockConnectionError)


@pytest.fixture
def live_keys():
    if os.name == "nt":
        fh = os.path.join(os.environ["USERPROFILE"], ".oclc/nyp_wc_test.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["WCKey"] = data["key"]
            os.environ["WCSecret"] = data["secret"]
            os.environ["WCScopes"] = " ".join(data["scopes"])

    else:
        # Travis env variables defined in the repository settings
        pass


@pytest.fixture
def mock_token(mock_credentials, mock_successful_post_token_response):
    return WorldcatAccessToken(**mock_credentials)


@pytest.fixture
def mock_successful_session_get_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulSessionResponse()

    monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def mock_400_response(monkeypatch):
    def mock_api_response(*args, **kwargs):
        msg = {
            "type": "MISSING_QUERY_PARAMETER",
            "title": "Validation Failure",
            "detail": "detail here",
        }
        url = "https://test.org/some_endpoint"
        return MockServiceErrorResponse(code=400, json_response=msg, url=url)

    monkeypatch.setattr(requests.Session, "get", mock_api_response)
