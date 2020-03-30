# -*- coding: utf-8 -*-

import requests

from . import __version__


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

    def get_token(self):
        """Fetches OCLC access token"""
        token_url = f"{self.oauth_server}/token"
        headers = {"user-agent": f"bookops-worldcat/{__version__}"}
        auth = (self.key, self.secret)
        data = {"grant_type": self.grant_type, "scope": self.options["scope"]}
        req = requests.post(
            token_url, auth=auth, headers=headers, data=data, timeout=self.timeout
        )
        return req
