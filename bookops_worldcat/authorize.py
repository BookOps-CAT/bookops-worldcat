# -*- coding: utf-8 -*-

"""
This module provides means to authenticate and obtain a WorldCat access token.
"""

import datetime
import sys
from typing import Dict, Optional, Tuple, Union

import requests

from . import __title__, __version__
from .errors import WorldcatAuthorizationError


class WorldcatAccessToken:
    """
    Requests Worldcat access token.
    Authenticates and authorizes using Client Credentials Grant. Does not support
    Explicit Authorization Code and Refresh Token flows. Token with correctly
    bonded scopes can then be passed into a session of particular web service
    to authorize requests for resources.
    More on OCLC's client credentials grant:
    https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html

    Args:
        key:                    your WSKey public client_id
        secret:                 your WSKey secret
        scopes:                 request scopes for the access token as a string,
                                separate different scopes with space
        principal_id:           principalID (required for read/write endpoints)
        principal_idns:         principalIDNS (required for read/write endpoints)
        agent:                  "User-agent" parameter to be passed in the request
                                header; usage strongly encouraged
        timeout:                how long to wait for server to send data before
                                giving up; default value is 3 seconds


    Examples:
        >>> from bookops_worldcat import WorldcatAccessToken
        >>> token = WorldcatAccessToken(
                key="my_WSKey_client_id",
                secret="my_WSKey_secret",
                scope="WorldCatMetadataAPI",
                principal_id="your principalID here",
                principal_idns="your principalIDNS here",
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
        key: str,
        secret: str,
        scopes: str,
        principal_id: str,
        principal_idns: str,
        agent: str = "",
        timeout: Optional[
            Union[int, float, Tuple[int, int], Tuple[float, float]]
        ] = None,
    ) -> None:
        """Constructor"""

        self.agent = agent
        self.grant_type = "client_credentials"
        self.key = key
        self.oauth_server = "https://oauth.oclc.org"
        self.principal_id = principal_id
        self.principal_idns = principal_idns
        self.scopes = scopes
        self.secret = secret
        self.server_response: Optional[requests.Response] = None
        self.timeout = timeout
        self.token_expires_at: Optional[datetime.datetime] = None
        self.token_str = ""
        self.token_type = ""

        # default bookops-worldcat request header
        if not self.agent:
            self.agent = f"{__title__}/{__version__}"
        else:
            if not isinstance(self.agent, str):
                raise WorldcatAuthorizationError("Argument 'agent' must be a string.")

        # asure passed arguments are valid
        if not self.key:
            raise WorldcatAuthorizationError("Argument 'key' is required.")
        else:
            if not isinstance(self.key, str):
                raise WorldcatAuthorizationError("Argument 'key' must be a string.")

        if not self.secret:
            raise WorldcatAuthorizationError("Argument 'secret' is required.")
        else:
            if not isinstance(self.secret, str):
                raise WorldcatAuthorizationError("Argument 'secret' must be a string.")

        if not self.principal_id:
            raise WorldcatAuthorizationError(
                "Argument 'principal_id' is required for read/write endpoint of "
                "Metadata API."
            )
        if not self.principal_idns:
            raise WorldcatAuthorizationError(
                "Argument 'principal_idns' is required for read/write endpoint of "
                "Metadata API."
            )

        # validate passed scopes
        if not self.scopes:
            raise WorldcatAuthorizationError("Argument 'scopes' is required.")
        elif not isinstance(self.scopes, str):
            raise WorldcatAuthorizationError("Argument 'scopes' must a string.")
        self.scopes = self.scopes.strip()

        # assign default value for timout
        if not self.timeout:
            self.timeout = (3, 3)

        # initiate request
        self._request_token()

    def _auth(self) -> Tuple[str, str]:
        return (self.key, self.secret)

    def _hasten_expiration_time(self, utc_stamp_str: str) -> datetime.datetime:
        """
        Resets expiration time one second earlier to account
        for any delays between expiration check and request for
        new token in session setting.

        Args:
            utcstamp:               utc timestamp string

        Returns:
            utcstamp
        """
        utcstamp = datetime.datetime.strptime(
            utc_stamp_str, "%Y-%m-%d %H:%M:%SZ"
        ) - datetime.timedelta(seconds=1)
        utcstamp = utcstamp.replace(tzinfo=datetime.timezone.utc)
        return utcstamp

    def _parse_server_response(self, response: requests.Response) -> None:
        """Parses authorization server response"""
        self.server_response = response
        if response.status_code == requests.codes.ok:
            self.token_str = response.json()["access_token"]
            self.token_expires_at = self._hasten_expiration_time(
                response.json()["expires_at"]
            )
            self.token_type = response.json()["token_type"]
        else:
            raise WorldcatAuthorizationError(response.content)

    def _payload(self) -> Dict[str, str]:
        """Preps requests params"""
        return {
            "grant_type": self.grant_type,
            "scope": self.scopes,
            "principalID": self.principal_id,
            "principalIDNS": self.principal_idns,
        }

    def _post_token_request(self) -> requests.Response:
        """
        Fetches Worldcat access token for specified scope (web service)

        Returns:
            requests.models.Response
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
            raise WorldcatAuthorizationError(f"Trouble connecting: {sys.exc_info()[0]}")
        except Exception:
            raise WorldcatAuthorizationError(f"Unexpected error: {sys.exc_info()[0]}")

    def _request_token(self):
        """
        Initiates access token request and parses the response if successful.
        """
        response = self._post_token_request()
        self._parse_server_response(response)

    def _token_headers(self) -> Dict[str, str]:
        return {"User-Agent": self.agent, "Accept": "application/json"}

    def _token_url(self) -> str:
        return f"{self.oauth_server}/token"

    def is_expired(self) -> bool:
        """
        Checks if the access token is expired.

        Returns:
            bool

        Example:
        >>> token.is_expired()
        False
        """
        if isinstance(self.token_expires_at, datetime.datetime):
            if self.token_expires_at < datetime.datetime.now(datetime.timezone.utc):
                return True
            else:
                return False
        else:
            raise TypeError

    def __repr__(self):
        return (
            f"access_token: '{self.token_str}', "
            f"expires_at: '{self.token_expires_at:%Y-%m-%d %H:%M:%SZ}'"
        )
