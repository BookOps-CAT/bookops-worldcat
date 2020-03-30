import pytest

import requests

from bookops_worldcat.authorize import AuthorizeAccess


# class MockGetTokenResponse:
#     @staticmethod
#     def json():
#         return {
#             "access_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
#             "token_type": "bearer",
#             "expires_in": "1199",
#             "principalID": "",
#             "principalIDNS": "",
#             "scopes": "configPlatform context:128807",
#             "contextInstitutionId": "128807",
#             "expires_at": "2013-08-23 18:45:29Z",
#         }

#     # def text():
#     #     # returned text here


@pytest.fixture()
def mock_credentials():
    return {
        "name": "TestCreds",
        "library": "OCLC",
        "key": "WSkey",
        "secret": "WSsecret",
        "authenticating_institution_id": "123456",
        "context_institution_id": "00001",
        "principal_id": "00000000-111a-222b-333c-4d444444444d",
        "principal_idns": "urn:oclc:platform:00001",
        "scope": ["scope1", "scope2"],
        "oauth_server": "https://oauth.oclc.test.org",
    }


# class TestAuthorizeAccessViaClientCredentials:
#     @staticmethod
#     def get_token(mock_credentials):
#         cred = mock_credentials
#         return AuthorizeAccess(
#             oauth_server=cred["oauth_server"],
#             grant_type="client_credentials",
#             key=cred["key"],
#             secret=cred["secret"],
#             options={
#                 "scope": cred["scope"],
#                 "authenticating_institution_id": cred["authenticating_institution_id"],
#                 "context_institution_id": cred["context_institution_id"],
#             }
#         )

# @pytest.fixture
# def mock_access_via_client_creds(monkeypatch):
#     def


# @pytest.fixture
# def mock_post_token_response(monkeypatch):
#     """Requests.post() on OCLC token service"""

#     def mock_post(*args, **kwargs):
#         return MockGetTokenResponse()

#     monkeypatch.setattr(requests, "post", mock_post)


# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     """Removes requests.session.Session.request from all test."""
#     monkeypatch.delattr("requests.session.Session.request")
