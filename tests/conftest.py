import pytest

import requests

from bookops_worldcat.authorize import WorldcatAccessToken


@pytest.fixture()
def mock_access_token_response_json():
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


@pytest.fixture()
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
            "scope": ["scope1", "scope2"],
        },
        "oauth_server": "https://oauth.oclc.test.org",
    }


@pytest.fixture()
def mock_access_initiation_via_credentials(mock_credentials):
    cred = mock_credentials
    access = WorldcatAccessToken(
        oauth_server=cred["oauth_server"],
        grant_type="client_credentials",
        key=cred["key"],
        secret=cred["secret"],
        options=cred["options"],
    )
    return access


class MockTokenResponseViaCredentials:

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
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


@pytest.fixture
def mock_post_token_response(monkeypatch):
    def mock_post_token(*args, **kwargs):
        return MockTokenResponseViaCredentials()

    monkeypatch.setattr(requests, "post", mock_post_token)
