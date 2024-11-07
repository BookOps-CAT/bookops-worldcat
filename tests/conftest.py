# -*- coding: utf-8 -*-

import datetime
import json
import os
from typing import Dict, Generator, Union
import pytest
import requests

from bookops_worldcat import WorldcatAccessToken, MetadataSession


@pytest.fixture
def live_keys():
    if os.name == "nt" and not os.getenv("GITHUB_ACTIONS"):
        fh = os.path.join(os.environ["USERPROFILE"], ".oclc/nyp_wc_test.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["WCKey"] = data["key"]
            os.environ["WCSecret"] = data["secret"]
            os.environ["WCScopes"] = data["scopes"]


@pytest.fixture
def stub_marc_xml() -> str:
    stub_marc_xml = "<record><leader>00000nam a2200000 a 4500</leader><controlfield tag='008'>120827s2012    nyua          000 0 eng d</controlfield><datafield tag='010' ind1=' ' ind2=' '><subfield code='a'>   63011276 </subfield></datafield><datafield tag='035' ind1=' ' ind2=' '><subfield code='a'>ocn850940548</subfield></datafield><datafield tag='040' ind1=' ' ind2=' '><subfield code='a'>OCWMS</subfield><subfield code='b'>eng</subfield><subfield code='c'>OCWMS</subfield></datafield><datafield tag='100' ind1='0' ind2=' '><subfield code='a'>OCLC Developer Network</subfield></datafield><datafield tag='245' ind1='1' ind2='0'><subfield code='a'>Test Record</subfield></datafield><datafield tag='500' ind1=' ' ind2=' '><subfield code='a'>FOR OCLC DEVELOPER NETWORK DOCUMENTATION</subfield></datafield></record>"
    return stub_marc_xml


@pytest.fixture
def stub_holding_xml() -> str:
    stub_holding_xml = "<record><leader>00000nx  a2200000zi 4500</leader><controlfield tag='004'>312010</controlfield><controlfield tag='007'>zu</controlfield><controlfield tag='008'>1103280p    0   4001uueng0210908</controlfield><datafield ind2=' ' ind1=' ' tag='852'><subfield code='a'>OCWMS</subfield><subfield code='b'>EAST</subfield><subfield code='c'>EAST-STACKS</subfield></datafield><datafield ind2=' ' ind1=' ' tag='876'><subfield code='p'>879456</subfield></datafield></record>"
    return stub_holding_xml


@pytest.fixture
def stub_marc21() -> bytes:
    return b"00266nam a2200097 a 4500008004100000010001700041040002200058100002700080245001600107500004500123\x1e120827s2012    nyua          000 0 eng d\x1e  \x1fa   63011276 \x1e  \x1faOCWMS\x1fbeng\x1fcOCWMS\x1e0 \x1faOCLC Developer Network\x1e10\x1faTest Record\x1e  \x1faFOR OCLC DEVELOPER NETWORK DOCUMENTATION\x1e\x1d"


class FakeUtcNow(datetime.datetime):
    @classmethod
    def now(cls, tzinfo=datetime.timezone.utc):
        return cls(2020, 1, 1, 17, 0, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture
def mock_now(monkeypatch):
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


class MockAuthServerResponseSuccess:
    """Simulates auth server response to successful token request"""

    def __init__(self) -> None:
        self.status_code = 200

    def json(self) -> Dict[str, str]:
        expires_at = datetime.datetime.strftime(
            datetime.datetime.now() + datetime.timedelta(0, 1199),
            "%Y-%m-%d %H:%M:%SZ",
        )

        return {
            "access_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
            "token_type": "bearer",
            "expires_in": "1199",
            "principalID": "",
            "principalIDNS": "",
            "scope": "scope1",
            "scopes": "scope1",
            "contextInstitutionId": "00001",
            "expires_at": expires_at,
        }


class MockAuthServerResponseFailure:
    """Simulates auth server response to successful token request"""

    def __init__(self) -> None:
        self.status_code = 403
        self.content = b""

    def json(self) -> Dict[str, Union[str, int]]:
        return {
            "code": 403,
            "message": "Invalid scope(s): invalid (invalid) [Invalid service specified, Not on key]",
        }


class MockServiceErrorResponse:
    """Simulates web service error responses"""

    def __init__(self, code, json_response, url) -> None:
        self.status_code = code
        self.msg = json_response
        self.url = url
        self.text = f"{json_response}"

    def json(self) -> Dict[str, str]:
        return self.msg


class MockUnexpectedException:
    def __init__(self, *args, **kwargs) -> None:
        raise Exception


class MockTimeout:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.Timeout


class MockConnectionError:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.ConnectionError


class MockRetryError:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.RetryError


class MockHTTPSessionResponse(requests.Response):
    def __init__(self, http_code) -> None:
        self.status_code = http_code
        self.reason = "'foo'"
        self.url = "https://foo.bar?query"
        self._content = b"spam"


@pytest.fixture
def mock_session_response(request, monkeypatch):
    """
    Use together with `pytest.mark.http_code` marker to pass
    specific HTTP code to be returned to simulate various
    responses from different endpoints
    """
    marker = request.node.get_closest_marker("http_code")
    if marker is None:
        http_code = 200
    else:
        http_code = marker.args[0]

    def mock_api_response(*args, http_code=http_code, **kwargs):
        return MockHTTPSessionResponse(http_code=http_code)

    monkeypatch.setattr(requests.Session, "send", mock_api_response)


@pytest.fixture
def mock_credentials() -> Dict[str, str]:
    return {
        "key": "my_WSkey",
        "secret": "my_WSsecret",
        "scopes": "scope1 scope2",
    }


@pytest.fixture
def mock_oauth_server_response(
    mock_now, *args, **kwargs
) -> MockAuthServerResponseSuccess:
    return MockAuthServerResponseSuccess()


@pytest.fixture
def mock_successful_post_token_response(mock_now, monkeypatch):
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
    monkeypatch.setattr("requests.Session.send", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.post", MockTimeout)
    monkeypatch.setattr("requests.get", MockTimeout)
    monkeypatch.setattr("requests.Session.send", MockTimeout)


@pytest.fixture
def mock_connection_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockConnectionError)
    monkeypatch.setattr("requests.get", MockConnectionError)
    monkeypatch.setattr("requests.Session.send", MockConnectionError)


@pytest.fixture
def mock_retry_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockRetryError)
    monkeypatch.setattr("requests.get", MockRetryError)
    monkeypatch.setattr("requests.Session.send", MockRetryError)


@pytest.fixture
def mock_token(
    mock_credentials, mock_successful_post_token_response
) -> WorldcatAccessToken:
    return WorldcatAccessToken(**mock_credentials)


@pytest.fixture
def stub_session(mock_token) -> Generator[MetadataSession, None, None]:
    with MetadataSession(authorization=mock_token) as session:
        yield session


@pytest.fixture
def stub_retry_session(mock_token) -> Generator[MetadataSession, None, None]:
    with MetadataSession(
        authorization=mock_token,
        totalRetries=3,
        backoffFactor=0.5,
        statusForcelist=[500, 502, 503, 504],
        allowedMethods=["GET", "POST", "PUT"],
    ) as session:
        yield session
