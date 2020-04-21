from datetime import datetime, timedelta

import pytest

from bookops_worldcat import __title__, __version__
from bookops_worldcat.authorize import WorldcatAccessToken


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
            "scope": ["scope1", "scope2", "wcapi"],
        },
        "oauth_server": "https://oauth.oclc.org.test",
    }


class TestWorldcatAccessToken:
    """Test WorldcatAccessToken and obraining token"""

    def test_get_token_url(
        self, mock_token_initiation_via_credentials, mock_credentials
    ):
        token = mock_token_initiation_via_credentials
        assert token._get_token_url() == f"{mock_credentials['oauth_server']}/token"

    def test_get_token_headers(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        assert token._get_post_token_headers() == {
            "user-agent": f"{__title__}/{__version__}",
            "Accept": "application/json",
        }

    def test_get_auth(self, mock_token_initiation_via_credentials, mock_credentials):
        token = mock_token_initiation_via_credentials
        assert token._get_auth() == ("WSkey", "WSsecret")

    def test_get_data(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        assert token._get_payload() == {
            "grant_type": "client_credentials",
            "scope": "scope1 scope2",
            "principalID": "00000000-111a-222b-333c-4d444444444d",
            "principalIDNS": "urn:oclc:platform:00001",
        }

    def test_successful_token_initiation_via_credentials(
        self, mock_credentials, mock_successful_post_token_request,
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            oauth_server=creds["oauth_server"],
            key=creds["key"],
            secret=creds["secret"],
            options=creds["options"],
        )

        assert token.oauth_server == creds["oauth_server"]
        assert token.key == creds["key"]
        assert token.secret == creds["secret"]
        assert token.grant_type == "client_credentials"
        assert token.options["scope"] == ["scope1", "scope2"]
        assert token.options["principal_id"] == "00000000-111a-222b-333c-4d444444444d"
        assert token.options["principal_idns"] == "urn:oclc:platform:00001"
        assert token.timeout == (5, 5)
        assert token.token_str == "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
        assert token.token_expires_at == "2013-08-23 18:45:29Z"
        assert token.token_type == "bearer"

    def test_failed_token_initiation_via_credentials(
        self, mock_credentials, mock_failed_post_token_request
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            oauth_server=creds["oauth_server"],
            key=creds["key"],
            secret=creds["secret"],
            options=creds["options"],
        )

        assert token.oauth_server == creds["oauth_server"]
        assert token.key == creds["key"]
        assert token.secret == creds["secret"]
        assert token.grant_type == "client_credentials"
        assert token.options == creds["options"]
        assert token.timeout == (5, 5)
        assert token.error_code == 401
        assert token.error_message == "some error message"
        assert token.token_str is None
        assert token.token_expires_at is None
        assert token.token_type is None

    def test_token_initiation_via_credentials_missing_scope_option(
        self, mock_credentials
    ):
        creds = mock_credentials
        creds["options"].pop("scope", None)
        with pytest.raises(KeyError):
            WorldcatAccessToken(
                oauth_server=creds["oauth_server"],
                key=creds["key"],
                secret=creds["secret"],
                options=creds["options"],
            )

    def test_token_initiation_via_credentials_missing_principal_id_option(
        self, mock_credentials
    ):
        creds = mock_credentials
        creds["options"].pop("principal_id", None)
        with pytest.raises(KeyError):
            WorldcatAccessToken(
                oauth_server=creds["oauth_server"],
                key=creds["key"],
                secret=creds["secret"],
                options=creds["options"],
            )

    def test_token_initiation_via_credentials_missing_context_institution_id_option(
        self, mock_credentials
    ):
        creds = mock_credentials
        creds["options"].pop("principal_idns", None)
        with pytest.raises(KeyError):
            WorldcatAccessToken(
                oauth_server=creds["oauth_server"],
                key=creds["key"],
                secret=creds["secret"],
                options=creds["options"],
            )

    def test_token_initiation_via_credentials_missing_oauth_server_argument(
        self, mock_credentials
    ):
        creds = mock_credentials
        with pytest.raises(ValueError):
            WorldcatAccessToken(
                oauth_server=None,
                key=creds["key"],
                secret=creds["secret"],
                options=creds["options"],
            )

        with pytest.raises(ValueError):
            WorldcatAccessToken(
                oauth_server="",
                key=creds["key"],
                secret=creds["secret"],
                options=creds["options"],
            )
        with pytest.raises(ValueError):
            WorldcatAccessToken(
                key=creds["key"], secret=creds["secret"], options=creds["options"],
            )

    def test_token_initiation_via_credentials_missing_key_argument(
        self, mock_credentials
    ):
        creds = mock_credentials
        with pytest.raises(ValueError):
            WorldcatAccessToken(
                oauth_server=creds["oauth_server"],
                key="",
                secret=creds["secret"],
                options=creds["options"],
            )

    def test_token_initiation_via_credentials_missing_secret_argument(
        self, mock_credentials
    ):
        creds = mock_credentials
        with pytest.raises(ValueError):
            WorldcatAccessToken(
                oauth_server=creds["oauth_server"],
                key=creds["key"],
                options=creds["options"],
            )

    def test_token_is_expired_is_true(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        assert token.token_expires_at == "2013-08-23 18:45:29Z"
        assert token.is_expired() is True

    def test_token_is_expired_is_false(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.token_expires_at = datetime.strftime(
            datetime.utcnow() + timedelta(0, 60), "%Y-%m-%d %H:%M:%SZ"
        )
        assert token.is_expired() is False
