# -*- coding: utf-8 -*-

from datetime import datetime
import sys

import requests


from . import __title__, __version__
from .errors import WorldcatAuthorizationError


class WorldcatAccessToken:
    """
    Requests Worldcat access token. Authenticates and authorizes using Client
    Credentials Grant. Does not support Explicit Authorization Code and Refresh
    Token flows. Token with correctly bonded scopes can then be passed into a session
    of particular web service to authorize following requests for resources.
    More on OCLC's web services authorization:
    https://www.oclc.org/developer/develop/authentication/oauth/client-credentials-grant.en.html

    Args:
        key: str,                               your WSKey public client_id
        secret: str,                            your WSKey secret
        scopes: str or list                     request scopes for the access token
        agent: (optional) str,                  "User-agent" parameter to be passed
                                                in the request header; usage strongly
                                                encouraged
        timeout: (optional) float or tuple,     how long to wait for server to send
                                                data before giving up; default value
                                                is 3 seconds

    Returns:
        token, class


    Basic usage:
        >>> from bookops_worldcat import WorldcatAccessToken
        >>> token = WorldcatAccessToken(
                key="my_WSKey_client_id",
                secret="my_WSKey_secret",
                scope="WorldCatMetadataAPI",
                agent="my_app/1.0.0")
        >>> token.token_str
        "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
        >>> token.is_expired()
        False
        >>> token.server_response.json()
        {"token_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
         "token_type": "bearer",
         "expires_in": "1199",
         "principalID": "",
         "principalIDNS": "",
         "scopes": "WorldCatMetadataAPI",
         "contextInstitutionId": "00001",
         "expires_at": "2020-08-23 18:45:29Z"}
        >>> token.server_response.request.headers
        {"User-Agent": "my_app/1.0.0",
         "Accept-Encoding": "gzip, deflate",
         "Accept": "application/json",
         "Connection": "keep-alive",
         "Content-Length": "67",
         "Content-Type": "application/x-www-form-urlencoded",
         "Authorization": "Basic encoded_authorization_here="}

    """

    def __init__(
        self,
        key=None,
        secret=None,
        scopes=[],
        agent=None,
        timeout=None,
    ):
        """Constructor"""

        self.agent = agent
        self.grant_type = "client_credentials"
        self.key = key
        self.oauth_server = "https://oauth.oclc.org"
        self.scopes = scopes
        self.secret = secret
        self.server_response = None
        self.timeout = timeout
        self.token_expires_at = None
        self.token_str = None
        self.token_type = None

        # default bookops-worldcat request header
        if self.agent is None:
            self.agent = f"{__title__}/{__version__}"
        else:
            if type(self.agent) is not str:
                raise WorldcatAuthorizationError("Argument 'agent' must be a string.")

        # asure passed arguments are valid
        if not self.key:
            raise WorldcatAuthorizationError("Argument 'key' is required.")
        else:
            if type(self.key) is not str:
                raise WorldcatAuthorizationError("Argument 'key' must be a string.")

        if not self.secret:
            raise WorldcatAuthorizationError("Argument 'secret' is required.")
        else:
            if type(self.secret) is not str:
                raise WorldcatAuthorizationError("Argument 'secret' must be a string.")

        # validate passed scopes
        if type(self.scopes) is list:
            self.scopes = " ".join(self.scopes)
        elif type(self.scopes) is not str:
            raise WorldcatAuthorizationError(
                "Argument 'scope' must a string or a list."
            )
        self.scopes = self.scopes.strip()
        if self.scopes == "":
            raise WorldcatAuthorizationError("Argument 'scope' is missing.")

        # assign default value for timout
        if not self.timeout:
            self.timeout = (3, 3)

        # initiate request
        self.request_token()

    def _token_url(self):
        return f"{self.oauth_server}/token"

    def _token_headers(self):
        return {"User-Agent": self.agent, "Accept": "application/json"}

    def _auth(self):
        return (self.key, self.secret)

    def _payload(self):
        return {"grant_type": self.grant_type, "scope": self.scopes}

    def _parse_server_response(self, response):
        self.server_response = response
        if response.status_code == requests.codes.ok:
            self.token_str = response.json()["access_token"]
            self.token_expires_at = response.json()["expires_at"]
            self.token_type = response.json()["token_type"]
        else:
            raise WorldcatAuthorizationError(response.json())

    def _post_token_request(self):
        """
        Fetches Worldcat access token for specified scope (web service)

        Returns:
            server_response: instance of requests.Response
        """

        token_url = self._token_url()
        headers = self._token_headers()
        auth = self._auth()
        payload = self._payload()
        try:
            response = requests.post(
                token_url,
                auth=auth,
                headers=headers,
                params=payload,
                timeout=self.timeout,
            )
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise WorldcatAuthorizationError(f"Trouble connecing: {sys.exc_info()[0]}")
        except Exception:
            raise WorldcatAuthorizationError(f"Unexpected error: {sys.exc_info()[0]}")

    def request_token(self):
        """
        Initiates access token request and parses the response if successful.
        """
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
