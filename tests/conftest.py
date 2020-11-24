# -*- coding: utf-8 -*-

import datetime
import json
import os

import pytest
import requests


from bookops_worldcat import WorldcatAccessToken


class FakeUtcNow(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return cls(2020, 1, 1, 17, 0, 0, 0)


@pytest.fixture
def mock_utcnow(monkeypatch):
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


class MockAuthServerResponseSuccess:
    """Simulates auth server response to successful token request"""

    def __init__(self):
        self.status_code = 200

    def json(self):
        expires_at = datetime.datetime.strftime(
            datetime.datetime.utcnow() + datetime.timedelta(0, 1199),
            "%Y-%m-%d %H:%M:%SZ",
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
        self.text = f"{json_response}"

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


class MockSuccessfulHTTP200SessionResponse:
    def __init__(self):
        self.status_code = 200


class MockSuccessfulHTTP201SessionResponse:
    def __init__(self):
        self.status_code = 201


class MockSuccessfulHTTP207SessionResponse:
    def __init__(self):
        self.status_code = 207


@pytest.fixture
def mock_credentials():
    return {
        "key": "my_WSkey",
        "secret": "my_WSsecret",
        "scopes": ["scope1", "scope2"],
        "principal_id": "my_principalID",
        "principal_idns": "my_principalIDNS",
    }


@pytest.fixture
def mock_oauth_server_response(mock_utcnow, *args, **kwargs):
    return MockAuthServerResponseSuccess()


@pytest.fixture
def mock_successful_post_token_response(mock_utcnow, monkeypatch):
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
    monkeypatch.setattr("requests.Session.post", MockUnexpectedException)
    monkeypatch.setattr("requests.Session.delete", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.post", MockTimeout)
    monkeypatch.setattr("requests.get", MockTimeout)
    monkeypatch.setattr("requests.Session.get", MockTimeout)
    monkeypatch.setattr("requests.Session.post", MockTimeout)
    monkeypatch.setattr("requests.Session.delete", MockTimeout)


@pytest.fixture
def mock_connectionerror(monkeypatch):
    monkeypatch.setattr("requests.post", MockConnectionError)
    monkeypatch.setattr("requests.get", MockConnectionError)
    monkeypatch.setattr("requests.Session.get", MockConnectionError)
    monkeypatch.setattr("requests.Session.post", MockConnectionError)
    monkeypatch.setattr("requests.Session.delete", MockConnectionError)


@pytest.fixture
def live_keys():
    if os.name == "nt":
        fh = os.path.join(os.environ["USERPROFILE"], ".oclc/nyp_wc_test.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["WCKey"] = data["key"]
            os.environ["WCSecret"] = data["secret"]
            os.environ["WCScopes"] = " ".join(data["scopes"])
            os.environ["WCPrincipalID"] = data["principal_id"]
            os.environ["WCPrincipalIDNS"] = data["principal_idns"]

    else:
        # Travis env variables defined in the repository settings
        pass


@pytest.fixture
def mock_token(mock_credentials, mock_successful_post_token_response):
    return WorldcatAccessToken(**mock_credentials)


@pytest.fixture
def mock_successful_session_get_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP200SessionResponse()

    monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def mock_successful_session_post_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP200SessionResponse()

    monkeypatch.setattr(requests.Session, "post", mock_api_response)


@pytest.fixture
def mock_successful_holdings_post_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP201SessionResponse()

    monkeypatch.setattr(requests.Session, "post", mock_api_response)


@pytest.fixture
def mock_successful_holdings_delete_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP200SessionResponse()

    monkeypatch.setattr(requests.Session, "delete", mock_api_response)


@pytest.fixture
def mock_successful_multi_status_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP207SessionResponse()

    monkeypatch.setattr(requests.Session, "get", mock_api_response)
    monkeypatch.setattr(requests.Session, "post", mock_api_response)
    monkeypatch.setattr(requests.Session, "delete", mock_api_response)


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


@pytest.fixture
def mock_409_response(monkeypatch):
    def mock_api_response(*args, **kwargs):
        msg = {
            "code": {"value": "WS-409", "type": "application"},
            "message": "Trying to set hold while holding already exists",
            "detail": None,
        }
        url = "https://test.org/some_endpoint"
        return MockServiceErrorResponse(code=409, json_response=msg, url=url)

    monkeypatch.setattr(requests.Session, "post", mock_api_response)
    monkeypatch.setattr(requests.Session, "delete", mock_api_response)
