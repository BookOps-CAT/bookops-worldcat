import pytest
import requests

from bookops_worldcat.authorize import WorldcatAccessToken


@pytest.fixture
def mock_credentials():
    return {
        "name": "TestCreds",
        "library": "OCLC",
        "key": "WSkey",
        "secret": "WSsecret",
        "options": {
            "authenticating_institution_id": "123456",
            "context_institution_id": "00001",
            "principal_id": "00000000-111a-222b-333c-4d444444444d",
            "principal_idns": "urn:oclc:platform:00001",
            "scope": ["scope1", "scope2", "wcapi"],
        },
        "oauth_server": "https://oauth.oclc.org.test",
    }


class MockAuthServerResponseObjSuccess:
    """Simulates auth server response to successful token request"""

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "access_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
            "token_type": "bearer",
            "expires_in": "1199",
            "principalID": "",
            "principalIDNS": "",
            "scopes": "SCOPE HERE",
            "contextInstitutionId": "00001",
            "expires_at": "2013-08-23 18:45:29Z",
        }


class MockAuthServerResponseObjFailure:
    """Simulates auth server resonse to failed token request"""

    def __init__(self):
        self.status_code = 401

    def json(self):
        return {"code": 401, "message": "some error message"}


@pytest.fixture
def mock_successful_post_token_request(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseObjSuccess()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_failed_post_token_request(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseObjFailure()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_token_initiation_via_credentials(
    mock_credentials, mock_successful_post_token_request
):
    cred = mock_credentials
    token = WorldcatAccessToken(
        oauth_server=cred["oauth_server"],
        key=cred["key"],
        secret=cred["secret"],
        options=cred["options"],
    )
    return token


class MockSuccessfulSessionResponse:
    def __init__(self):
        self.status_code = 200


@pytest.fixture
def mock_successful_session_get_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulSessionResponse()

    monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def mock_successful_session_post_request(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulSessionResponse()

    monkeypatch.setattr(requests.Session, "post", mock_api_response)
