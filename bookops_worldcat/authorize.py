# -*- coding: utf-8 -*-

from datetime import datetime

import requests

from . import __title__, __version__


class WorldcatAccessToken:
    """
    Requests OCLC API access token via Client Credentials only.
    Server response informaiton can be access using .server_response property.
    Does not support Explicit Authorization Code and Refresh Token flows.

    Args:
        oauth_server: str,  OCLC authorization server
        wskey: str,         OCLC API key
        wssecret: str,      OCLC API secret
        option: dict,       valid options:
                            - authenticating_institution_id
                            - context_institution_id
                            - scope

    Basic usage:
        >>> from bookops_worldcat import WorldcatAccessToken
        >>> token = WorldcatAccessToken(
                oauth_server='https://oauth.oclc.org',
                grant_type='client_credentials',
                key='WSkey',
                secret='WSsecret',
                options={"scope": ['scope1', 'scope2']}
            )
        >>> token.token_str
          "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
        >>> token.is_expired()
          False
        >>> # token object retains post request (requests.Request object) functinality
        >>> token.server_response.json()
        {"token_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
         "token_type": "bearer",
         "expires_in": "1199",
         "principalID": "",
         "principalIDNS": "",
         "scopes": "SCOPE HERE",
         "contextInstitutionId": "00001",
         "expires_at": "2013-08-23 18:45:29Z"}
        >>> token.server_response.request.headers
        {'user-agent': 'bookops-worldcat/0.1.0',
         'Accept-Encoding': 'gzip, deflate',
         'Accept': '*/*',
         'Connection': 'keep-alive',
         'Content-Length': '67',
         'Content-Type': 'application/x-www-form-urlencoded',
         'Authorization': 'Basic encoded_authorization_here='}
    """

    def __init__(
        self, oauth_server=None, key=None, secret=None, options=None,
    ):
        """Constructor."""

        self.error_code = None
        self.error_message = None
        self.grant_type = "client_credentials"
        self.institution_id = None
        self.key = key
        self.oauth_server = oauth_server
        self.options = options
        self.secret = secret
        self.timeout = (5, 5)
        self.token_expires_at = None
        self.token_str = None
        self.token_type = None
        self.server_response = None
        self.valid_options = [
            "authenticating_institution_id",
            "context_institution_id",
            "scope",
        ]

        if not self.oauth_server:
            raise ValueError("Argument oauth_server cannot be empty.")

        if not self.key:
            raise ValueError("Missing key argument.")

        if not self.secret:
            raise ValueError("Missing secret argument.")

        if (
            "scope" not in options
            or "authenticating_institution_id" not in options
            or "context_institution_id" not in options
        ):
            raise KeyError("Missing option required for client credential grant.")

        self.institution_id = options["authenticating_institution_id"]

        # post access token request & create token object
        self.create_token()

    def _get_token_url(self):
        return f"{self.oauth_server}/token"

    def _get_post_token_headers(self):
        return {
            "user-agent": f"{__title__}/{__version__}",
            "Accept": "application/json",
        }

    def _get_auth(self):
        return (self.key, self.secret)

    def _get_payload(self):
        return {
            "grant_type": self.grant_type,
            "scope": f"{self.options['scope'][0]}",
        }

    def _parse_server_response(self, response):
        self.server_response = response
        if response.status_code == requests.codes.ok:
            self.token_str = response.json()["access_token"]
            self.token_expires_at = response.json()["expires_at"]
            self.token_type = response.json()["token_type"]
            self.error_code = None
            self.error_message = None
        else:
            self.token_str = None
            self.token_expires_at = None
            self.token_type = None

            # !!! this should be wrapped into exceptions, response not always can be
            # serialized to json !!!
            self.error_code = response.json()["code"]
            self.error_message = response.json()["message"]

    def _post_token_request(self):
        """
        Fetches OCLC access token
        Returns:
            server_response: instance of requests.Response
        """
        token_url = self._get_token_url()
        headers = self._get_post_token_headers()
        auth = self._get_auth()
        payload = self._get_payload()
        response = requests.post(
            token_url, auth=auth, headers=headers, params=payload, timeout=self.timeout
        )
        return response

    def create_token(self):
        response = self._post_token_request()
        self._parse_server_response(response)

    def is_expired(self):
        if (
            datetime.strptime(self.token_expires_at, "%Y-%m-%d %H:%M:%SZ")
            < datetime.utcnow()
        ):
            return True
        else:
            return False
