# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatAccessToken:
    """
    Requests OCLC API access token via Client Credentials and Refresh Token flows.
    Does not support Explicit Authorization Code flow.

    Args:
        oauth_server: str,  OCLC authorization server
        grant_type: str,    "client_credentials" or refresh_token"
        wskey: str,         OCLC API key
        wssecret: str,      OCLC API secret
        option: dict,       valid options:
                            - authenticating_institution_id
                            - context_institution_id
                            - refresh_token
                            - scope

    Basic usage:
        >>> from bookops_worldcat import WorldcatAccessToken
        >>> access = WorldcatAccessToken(
                oauth_server='https://oauth.oclc.org',
                grant_type='client_credentials',
                key='WSkey',
                secret='WSsecret',
                options={"scope": ['scope1', 'scope2']}
            )
        >>> token = access.get_token()

    """

    def __init__(
        self, oauth_server=None, grant_type=None, key=None, secret=None, options=None,
    ):
        """Constructor."""

        self.oauth_server = oauth_server
        self.grant_type = grant_type
        self.key = key
        self.secret = secret
        self.options = options
        self.timeout = (5, 5)
        self.grant_types = ["client_credentials", "refresh_token"]
        self.valid_options = [
            "authenticating_institution_id",
            "context_institution_id",
            "refresh_token",
            "scope",
        ]

        if not self.oauth_server:
            raise ValueError("Argument oauth_server cannot be empty.")

        if self.grant_type not in self.grant_types:
            raise ValueError("Invalid grant_type passed.")

        if self.grant_type == "client_credentials" and (
            "scope" not in options
            or "authenticating_institution_id" not in options
            or "context_institution_id" not in options
        ):
            raise KeyError("Missing option required for client credential grant.")

        if not self.key:
            raise ValueError("Missing key argument.")

    def _get_token_url(self):
        return f"{self.oauth_server}/token"

    def _get_post_token_headers(self):
        return {"user-agent": f"{__title__}/{__version__}"}

    def _get_auth(self):
        return (self.key, self.secret)

    def _get_data(self):
        return {"grant_type": self.grant_type, "scope": self.options["scope"]}

    def get_token(self):
        """
        Fetches OCLC access token
        Returns:
            token_request_response: instance of requests.Response
        """
        token_url = self._get_token_url()
        headers = self._get_post_token_headers()
        auth = self._get_auth()
        data = self._get_data()
        response = requests.post(
            token_url, auth=auth, headers=headers, data=data, timeout=self.timeout
        )
        return response
