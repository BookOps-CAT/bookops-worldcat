# import requests
# import pytest

from bookops_worldcat import __version__
from bookops_worldcat.authorize import AuthorizeAccess


def test_mocked_credentials(mock_credentials):
    assert mock_credentials == {
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


class TestAuthorizeAccess:
    """Test AuthorizeAccess and obraining token"""

    def test_access_initiation_via_credentials(
        self, mock_access_initiation_via_credentials, mock_credentials
    ):
        creds = mock_credentials
        access = mock_access_initiation_via_credentials

        assert access.oauth_server == creds["oauth_server"]
        assert access.key == creds["key"]
        assert access.secret == creds["secret"]
        assert access.grant_type == "client_credentials"
        assert access.options == creds["options"]
        assert access.timeout == (5, 5)
        assert access.grant_types == ["client_credentials", "refresh_token"]

    def test_get_token_via_credentials(
        self,
        mock_access_initiation_via_credentials,
        mock_access_token_response_json,
        mock_post_token_response,
    ):
        access = mock_access_initiation_via_credentials

        results = access.get_token()
        assert results.json() == mock_access_token_response_json
