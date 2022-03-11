# -*- coding: utf-8 -*-

import datetime
import os

import pytest


from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat import __version__, __title__
from bookops_worldcat.errors import WorldcatAuthorizationError


class TestWorldcatAccessToken:
    """Tests WorldcatAccessToken object"""

    @pytest.mark.parametrize(
        "argm,expectation, msg",
        [
            (
                None,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'key' is required.",
            ),
            (
                "",
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'key' is required.",
            ),
            (
                124,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'key' must be a string.",
            ),
        ],
    )
    def test_key_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            WorldcatAccessToken(
                key=argm,
                secret="my_secret",
                scopes=["scope1"],
                principal_id="my_principalID",
                principal_idns="my_principalIDNS",
            )
            assert msg in str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'secret' is required.",
            ),
            (
                "",
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'secret' is required.",
            ),
            (
                123,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'secret' must be a string.",
            ),
        ],
    )
    def test_secret_exceptions(
        self, argm, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exp:
            WorldcatAccessToken(
                key="my_key",
                secret=argm,
                scopes=["scope1"],
                principal_id="my_principalID",
                principal_idns="my_principalIDNS",
            )
            assert msg in str(exp.value)

    def test_agent_exceptions(self, mock_successful_post_token_response):
        with pytest.raises(WorldcatAuthorizationError) as exp:
            WorldcatAccessToken(
                key="my_key",
                secret="my_secret",
                scopes="scope1",
                principal_id="my_principalID",
                principal_idns="my_principalIDNS",
                agent=124,
            )
            assert "Argument 'agent' must be a string." in str(exp.value)

    def test_agent_default_values(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
        )
        assert token.agent == f"{__title__}/{__version__}"

    @pytest.mark.parametrize(
        "arg,expectation,msg",
        [
            (
                None,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'principal_id' is required for read/write endpoint of Metadata API.",
            ),
            (
                "",
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'principal_id' is required for read/write endpoint of Metadata API.",
            ),
        ],
    )
    def test_principal_id_exception(
        self, arg, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exc:
            WorldcatAccessToken(
                key="my_key",
                secret="my_secret",
                scopes="scope1",
                principal_id=arg,
                principal_idns="my_principalIDNS",
            )
            assert msg in str(exc.value)

    @pytest.mark.parametrize(
        "arg,expectation,msg",
        [
            (
                None,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'principal_idns' is required for read/write endpoint of Metadata API.",
            ),
            (
                "",
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'principal_idns' is required for read/write endpoint of Metadata API.",
            ),
        ],
    )
    def test_principal_idns_exception(
        self, arg, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exc:
            WorldcatAccessToken(
                key="my_key",
                secret="my_secret",
                scopes="scope1",
                principal_id="my_principalID",
                principal_idns=arg,
            )
            assert msg in str(exc.value)

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'scope' must a string or a list.",
            ),
            (
                123,
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'scope' must a string or a list.",
            ),
            (
                " ",
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'scope' is missing.",
            ),
            (
                ["", ""],
                pytest.raises(WorldcatAuthorizationError),
                "Argument 'scope' is missing.",
            ),
        ],
    )
    def test_scope_exceptions(
        self, argm, expectation, msg, mock_successful_post_token_response
    ):
        with expectation as exp:
            WorldcatAccessToken(
                key="my_key",
                secret="my_secret",
                scopes=argm,
                principal_id="my_principalID",
                principal_idns="my_principalIDNS",
            )
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
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
            timeout=argm,
        )
        assert token.timeout == expectation

    @pytest.mark.parametrize(
        "argm,expectation",
        [("scope1", "scope1"), (["scope1", "scope2"], "scope1 scope2")],
    )
    def test_scope_manipulation(
        self, argm, expectation, mock_successful_post_token_response
    ):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes=argm,
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
        )
        assert token.scopes == expectation

    def test_token_url(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
        )
        assert token._token_url() == "https://oauth.oclc.org/token"

    def test_token_headers(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
            agent="foo",
        )
        assert token._token_headers() == {
            "User-Agent": "foo",
            "Accept": "application/json",
        }

    def test_auth(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
            agent="foo",
        )
        assert token._auth() == ("my_key", "my_secret")

    def test_hasten_expiration_time(self, mock_token):
        utc_stamp = "2020-01-01 17:19:59Z"
        token = mock_token
        assert token._hasten_expiration_time(utc_stamp) == "2020-01-01 17:19:58Z"

    def test_payload(self, mock_successful_post_token_response):
        token = WorldcatAccessToken(
            key="my_key",
            secret="my_secret",
            scopes="scope1",
            principal_id="my_principalID",
            principal_idns="my_principalIDNS",
            agent="foo",
        )
        assert token._payload() == {
            "grant_type": "client_credentials",
            "scope": "scope1",
            "principalID": "my_principalID",
            "principalIDNS": "my_principalIDNS",
        }

    def test_post_token_request_timout(self, mock_credentials, mock_timeout):
        creds = mock_credentials
        with pytest.raises(WorldcatAuthorizationError):
            WorldcatAccessToken(
                key=creds["key"],
                secret=creds["secret"],
                scopes=creds["scopes"],
                principal_id=creds["principal_id"],
                principal_idns=creds["principal_idns"],
            )

    def test_post_token_request_connectionerror(
        self, mock_credentials, mock_connection_error
    ):
        creds = mock_credentials
        with pytest.raises(WorldcatAuthorizationError):
            WorldcatAccessToken(
                key=creds["key"],
                secret=creds["secret"],
                scopes=creds["scopes"],
                principal_id=creds["principal_id"],
                principal_idns=creds["principal_idns"],
            )

    def test_post_token_request_unexpectederror(
        self, mock_credentials, mock_unexpected_error
    ):
        creds = mock_credentials
        with pytest.raises(WorldcatAuthorizationError):
            WorldcatAccessToken(
                key=creds["key"],
                secret=creds["secret"],
                scopes=creds["scopes"],
                principal_id=creds["principal_id"],
                principal_idns=creds["principal_idns"],
            )

    def test_invalid_post_token_request(
        self, mock_credentials, mock_failed_post_token_response
    ):
        creds = mock_credentials
        with pytest.raises(WorldcatAuthorizationError):
            WorldcatAccessToken(
                key=creds["key"],
                secret=creds["secret"],
                scopes=creds["scopes"],
                principal_id=creds["principal_id"],
                principal_idns=creds["principal_idns"],
            )

    def test_is_expired_false(
        self, mock_utcnow, mock_credentials, mock_successful_post_token_response
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"],
            secret=creds["secret"],
            scopes=creds["scopes"],
            principal_id=creds["principal_id"],
            principal_idns=creds["principal_idns"],
        )
        assert token.is_expired() is False

    def test_is_expired_true(
        self, mock_utcnow, mock_credentials, mock_successful_post_token_response
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"],
            secret=creds["secret"],
            scopes=creds["scopes"],
            principal_id=creds["principal_id"],
            principal_idns=creds["principal_idns"],
        )
        token.token_expires_at = datetime.datetime.strftime(
            datetime.datetime.utcnow() - datetime.timedelta(0, 1),
            "%Y-%m-%d %H:%M:%SZ",
        )

        assert token.is_expired() is True

    @pytest.mark.parametrize(
        "arg,expectation",
        [(None, pytest.raises(TypeError)), ("20-01-01", pytest.raises(ValueError))],
    )
    def test_is_expired_exception(
        self, arg, expectation, mock_credentials, mock_successful_post_token_response
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"],
            secret=creds["secret"],
            scopes=creds["scopes"],
            principal_id=creds["principal_id"],
            principal_idns=creds["principal_idns"],
        )
        token.token_expires_at = arg
        with expectation:
            token.is_expired()

    def test_post_token_request(
        self,
        mock_credentials,
        mock_successful_post_token_response,
        mock_oauth_server_response,
    ):
        creds = mock_credentials
        token = WorldcatAccessToken(
            key=creds["key"],
            secret=creds["secret"],
            scopes=creds["scopes"],
            principal_id=creds["principal_id"],
            principal_idns=creds["principal_idns"],
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

    def test_token_repr(
        self,
        mock_token,
        mock_utcnow,
    ):
        assert (
            str(mock_token)
            == "access_token: 'tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW', token_type: 'bearer', expires_at: '2020-01-01 17:19:58Z'"
        )

    @pytest.mark.webtest
    def test_cred_in_env_variables(self, live_keys):
        assert os.getenv("WCKey") is not None
        assert os.getenv("WCSecret") is not None
        assert os.getenv("WCScopes") == "WorldCatMetadataAPI"
        assert os.getenv("WCPrincipalID") is not None
        assert os.getenv("WCPrincipalIDNS") is not None

    @pytest.mark.webtest
    def test_post_token_request_with_live_service(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        assert token.server_response.status_code == 200

        # test presence of all returned parameters
        response = token.server_response.json()
        params = [
            "access_token",
            "expires_at",
            "authenticating_institution_id",
            "principalID",
            "context_institution_id",
            "scopes",
            "token_type",
            "expires_in",
            "principalIDNS",
        ]
        for p in params:
            assert p in response

        # test if any new additions are present
        assert sorted(params) == sorted(response.keys())

        # test if token looks right
        assert token.token_str is not None
        assert token.is_expired() is False
