# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class AuthorizeAccess:
    """
    Creates OCLC API access token
    Args:
        oauth_server: str,  OCLC authorization server
        grant_type: str,    "client_credentials" or refresh_token"
        wskey: str,         OCLC API key
        wssecret: str,      OCLC API secret
        option:     dict      valid options:

    Basic usage:
        >>> from bookops_worldcat import AccessToken
        >>> token = AccessToken()
    """

    def __init__(
        self, oauth_server=None, grant_type=None, key=None, secret=None, options=None,
    ):

        self.oauth_server = oauth_server
        self.grant_type = grant_type
        self.key = key
        self.secret = secret
        self.options = options
        self.timeout = (5, 5)
        self.grant_types = ["client_credentials", "refresh_token"]
        self.valid_options = [
            "authenticating_institution",
            "context_institution_id",
            "refresh_token",
            "scope",
        ]

    def _get_token_url(self):
        return f"{self.oauth_server}/token"

    def _get_post_token_headers(self):
        return {"user-agent": f"{__title__}/{__version__}"}

    def _get_auth(self):
        return (self.key, self.secret)

    def _get_data(self):
        return {"grant_type": self.grant_type, "scope": self.options["scope"]}

    def get_token(self):
        """Fetches OCLC access token"""
        token_url = self._get_token_url()
        headers = self._get_post_token_headers()
        auth = self._get_auth()
        data = self._get_data()
        req = requests.post(
            token_url, auth=auth, headers=headers, data=data, timeout=self.timeout
        )
        return req
