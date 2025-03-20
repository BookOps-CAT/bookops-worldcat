# -*- coding: utf-8 -*-

import datetime
import os

import pytest


from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat.errors import WorldcatAuthorizationError


class TestWorldcatAccessToken:
    """Tests WorldcatAccessToken object"""

    @pytest.mark.webtest
    def test_cred_in_env_variables(self, live_keys):
        assert os.getenv("WCKey") is not None
        assert os.getenv("WCSecret") is not None
        assert os.getenv("WCScopes") == "WorldCatMetadataAPI"

    @pytest.mark.webtest
    def test_post_token_request_with_live_service(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
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
            "scope",
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
        assert token.token_str.startswith("tk_")
        assert response["scopes"] == response["scope"]
        assert token.is_expired() is False
        assert isinstance(token.token_expires_at, datetime.datetime)

    @pytest.mark.webtest
    def test_post_token_request_with_live_service_no_timeout(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            timeout=None,
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
            "scope",
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
        assert token.token_str.startswith("tk_")
        assert response["scopes"] == response["scope"]
        assert token.is_expired() is False
        assert isinstance(token.token_expires_at, datetime.datetime)

    @pytest.mark.webtest
    def test_post_token_request_auth_error(self, live_keys):
        with pytest.raises(WorldcatAuthorizationError) as exp:
            token = WorldcatAccessToken(
                key=os.environ["WCKey"],
                secret="secret",
                scopes=os.environ["WCScopes"],
            )
            assert token.server_response.status_code == 401
        assert "No valid authentication credentials found in request" in str(exp.value)
