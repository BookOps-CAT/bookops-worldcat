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
                                users with WSKeys set up to act as multiple institutions
                                should provide scope and registryID in the format
                                "{scope} context:{registryID}"
                                examples:
                                    single institution WSKey:
                                        "WorldCatMetadataAPI"
                                    multi-institution WSKey:
                                        "WorldCatMetadataAPI context:00001"
        agent:                  "User-agent" parameter to be passed in the request
                                header; usage strongly encouraged
        timeout:                how long to wait for server to send data before
                                giving up; can accept different values for connect
                                and read timeouts. default value is 5 seconds for
                                read and 5 seconds for connect timeouts


    Examples:
        >>> from bookops_worldcat import WorldcatAccessToken
        >>> token = WorldcatAccessToken(
                key="my_WSKey_client_id",
                secret="my_WSKey_secret",
                scopes="WorldCatMetadataAPI",
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
        agent: str = "",
        timeout: Optional[Union[int, float, Tuple[int, int], Tuple[float, float]]] = (
            5,
            5,
        ),
    ) -> None:
        """Constructor"""

        self.agent = agent
        self.grant_type = "client_credentials"
        self.key = key
        self.oauth_server = "https://oauth.oclc.org"
        self.scopes = scopes
        self.secret = secret
        self.server_response: Optional[requests.Response] = None
        self.timeout = timeout
        self.token_expires_at: Optional[datetime.datetime] = None
        self.token_str = ""
        self.token_type = ""

        # default bookops-worldcat request header
        if isinstance(self.agent, str):
            if not self.agent.strip():
                self.agent = f"{__title__}/{__version__}"
        else:
            raise TypeError("Argument 'agent' must be a string.")

        # ensure passed arguments are valid
        if isinstance(self.key, str):
            if not self.key.strip():
                raise ValueError("Argument 'key' cannot be an empty string.")
        else:
            raise TypeError("Argument 'key' must be a string.")

        if isinstance(self.secret, str):
            if not self.secret.strip():
                raise ValueError("Argument 'secret' cannot be an empty string.")
        else:
            raise TypeError("Argument 'secret' must be a string.")

        # validate passed scopes
        if isinstance(self.scopes, str):
            if not self.scopes.strip():
                raise ValueError("Argument 'scopes' cannot be an empty string.")
        else:
            raise TypeError("Argument 'scopes' must a string.")
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

        Examples:
            >>> token.is_expired()
            False

        """
        if isinstance(self.token_expires_at, datetime.datetime):
            if self.token_expires_at < datetime.datetime.now(datetime.timezone.utc):
                return True
            else:
                return False
        else:
            raise TypeError(
                "Attribute 'WorldcatAccessToken.token_expires_at' is of invalid type. "
                "Expected `datetime.datetime` object."
            )

    def __repr__(self):
        return (
            f"access_token: '{self.token_str}', "
            f"expires_at: '{self.token_expires_at:%Y-%m-%d %H:%M:%SZ}'"
        )
