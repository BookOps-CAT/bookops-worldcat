# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os

import pytest

import requests

from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat import __version__, __title__
from bookops_worldcat.errors import TokenRequestError


class TestWorldcatAccessToken:
    """Tests WorldcatAccessToken object"""

    @pytest.mark.parametrize(
        "argm,expectation, msg",
        [
            (None, pytest.raises(ValueError), "Argument 'key' is required."),
            ("", pytest.raises(ValueError), "Argument 'key' is required."),
            (124, pytest.raises(TypeError), "Argument 'key' must be a string."),
        ],
    )
    def test_key_exceptions(
        self, argm, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exp:
            WorldcatAccessToken(key=argm, secret="my_secret", scopes=["scope1"])
            assert msg in str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (None, pytest.raises(ValueError), "Argument 'secret' is required."),
            ("", pytest.raises(ValueError), "Argument 'secret' is required."),
            (123, pytest.raises(TypeError), "Argument 'secret' must be a string."),
        ],
    )
    def test_secret_exceptions(
        self, argm, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exp:
            WorldcatAccessToken(key="my_key", secret=argm, scopes=["scope1"])
            assert msg in str(exp.value)

    def test_agent_exceptions(self, mock_successful_post_token_response):
        with pytest.raises(TypeError) as exp:
            WorldcatAccessToken(
                key="my_key", secret="my_secret", scopes="scope1", agent=124
            )
            assert "Argument 'agent' must be a string." in str(exp.value)

    def test_agent_default_values(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(key="my_key", secret="my_secret", scopes="scope1")
        assert token.agent == f"{__title__}/{__version__}"

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(TypeError),
                "Argument 'scope' must a string or a list.",
            ),
            (
                123,
                pytest.raises(TypeError),
                "Argument 'scope' must a string or a list.",
            ),
            (" ", pytest.raises(ValueError), "Argument 'scope' is missing."),
            (["", ""], pytest.raises(ValueError), "Argument 'scope' is missing."),
        ],
    )
    def test_scope_exceptions(
        self, argm, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exp:
            WorldcatAccessToken(key="my_key", secret="my_secret", scopes=argm)
            assert msg in str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (None, (3, 3)),
            (1, 1),
            (0.5, 0.5),
            ((5, 5), (5, 5)),
            ((0.1, 0.2), (0.1, 0.2)),
        ],
    )
    def test_timeout_argument(
        self, argm, expectation, mock_successful_post_token_response
    ):
        token = WorldcatAccessToken(
            key="my_key", secret="my_secret", scopes="scope1", timeout=argm
        )
        assert token.timeout == expectation

    @pytest.mark.parametrize(
        "argm,expectation",
        [("scope1", "scope1"), (["scope1", "scope2"], "scope1 scope2")],
    )
    def test_scope_manipulation(
        self, argm, expectation, mock_successful_post_token_response
    ):
        token = WorldcatAccessToken(key="my_key", secret="my_secret", scopes=argm)
        assert token.scopes == expectation

    def test_token_url(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(key="my_key", secret="my_secret", scopes="scope1")
        assert token._token_url() == "https://oauth.oclc.org/token"

    def test_token_headers(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key", secret="my_secret", scopes="scope1", agent="foo"
        )
        assert token._token_headers() == {
            "User-Agent": "foo",
            "Accept": "application/json",
        }

    def test_auth(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key", secret="my_secret", scopes="scope1", agent="foo"
        )
        assert token._auth() == ("my_key", "my_secret")

    def test_payload(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key", secret="my_secret", scopes="scope1", agent="foo"
        )
        assert token._payload() == {
            "grant_type": "client_credentials",
            "scope": "scope1",
        }

    def test_post_token_request_timeout(self, mock_credentials, mock_timeout):
        creds = mock_credentials
        with pytest.raises(requests.exceptions.Timeout):
            WorldcatAccessToken(
                key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
            )

    def test_post_token_request_connectionerror(
        self, mock_credentials, mock_connectionerror
    ):
        creds = mock_credentials
        with pytest.raises(requests.exceptions.ConnectionError):
            WorldcatAccessToken(
                key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
            )

    def test_invalid_post_token_request(
        self, mock_credentials, mock_failed_post_token_response
    ):
        creds = mock_credentials
        with pytest.raises(TokenRequestError):
            WorldcatAccessToken(
                key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
            )

    def test_is_expired_false(
        self, mock_credentials, mock_successful_post_token_response
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
        )
        assert token.is_expired() is False

    def test_is_expired_true(
        self, mock_credentials, mock_successful_post_token_response
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
        )
        token.token_expires_at = datetime.strftime(
            datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
        )

        assert token.is_expired() is True

    def test_post_token_request(
        self,
        mock_credentials,
        mock_successful_post_token_response,
        mock_oauth_server_response,
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"], secret=creds["secret"], scopes=creds["scopes"]
        )
        assert token.token_str == "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
        assert token.token_type == "bearer"
        assert token.grant_type == "client_credentials"
        assert token.key == creds["key"]
        assert token.secret == creds["secret"]
        assert token.oauth_server == "https://oauth.oclc.org"
        assert token.scopes == "scope1 scope2"
        assert token.server_response.json() == mock_oauth_server_response.json()
        assert token.timeout == (3, 3)

    def test_post_token_request_with_live_service(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        assert token.server_response.status_code == 200
        assert token.token_str is not None
        assert token.is_expired() is False
