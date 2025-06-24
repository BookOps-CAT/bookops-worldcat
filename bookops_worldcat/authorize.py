# -*- coding: utf-8 -*-

"""
Provides means to authenticate and authorize interactions with OCLC web services.
"""

import datetime
import sys
from typing import Optional, Union

import requests

from . import __title__, __version__
from .errors import WorldcatAuthorizationError


class WorldcatAccessToken:
    """
    Requests a WorldCat access token.

    Authenticates and authorizes using
    [Client Credentials Grant](https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html)
    flow. A token with correctly bonded scopes can be passed into a session of an
    OCLC web service to authorize requests for resources.

    Example:
        ```py
        from bookops_worldcat import WorldcatAccessToken

        token = WorldcatAccessToken(
            key="my_WSKey_client_id",
            secret="my_WSKey_secret",
            scopes="WorldCatMetadataAPI",
            agent="my_app/1.0.0")
        print(token.token_str)
        #>"tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
        print(token.is_expired())
        #>False
        print(token.server_response.json())
        {
            "token_token": "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
            "token_type": "bearer",
            "expires_in": "1199",
            "principalID": "",
            "principalIDNS": "",
            "scope": "WorldCatMetadataAPI",
            "scopes": "WorldCatMetadataAPI",
            "contextInstitutionId": "00001",
            "expires_at": "2020-08-23 18:45:29Z"
        }
        print(token.server_response.request.headers)
        {
            "User-Agent": "my_app/1.0.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
            "Connection": "keep-alive",
            "Content-Length": "67",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic encoded_authorization_here="
        }
        ```
    """  # noqa: E501

    def __init__(
        self,
        key: str,
        secret: str,
        scopes: str,
        agent: str = "",
        timeout: Union[
            int, float, tuple[Union[int, float], Union[int, float]], None
        ] = (5, 5),
    ) -> None:
        """Initializes WorldcatAccessToken object.


        info: Usage Documentation:
            - [Basic Usage](../start.md#authentication-and-authorization)
            - [Advanced Usage](../advanced.md#WorldcatAccessToken)

        Args:
            key:
                Your WSKey public client_id
            secret:
                Your WSKey secret
            scopes:
                Request scopes for the access token as a string. Multiple scopes
                should be separated with a space. Users with WSKeys set up to act on
                behalf of multiple institutions should provide scope and registryID
                in the format:
                `{scope} context:{registryID}`

                **EXAMPLES:**

                - Single institution WSKey: `"WorldCatMetadataAPI"`
                - Multi-institution WSKey: `"WorldCatMetadataAPI context:00001"`

            agent:
                `User-agent` parameter to be passed in the request header. Usage is
                strongly encouraged.
            timeout:
                How long to wait for server to send data before giving up. Accepts
                separate values for connect and read timeouts or a single value.

        Raises:
            TypeError:
                If `agent`, `key`, `secret`, or `scopes` args are passed
                anything other than a str.
            ValueError:
                If an empty str is passed to `key`, `secret` or `scopes` arg.
            WorldcatAuthorizationError:
                If request for token encounters any errors.
        """

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

        # initiate request
        self._request_token()

    def _auth(self) -> tuple[str, str]:
        return (self.key, self.secret)

    def _hasten_expiration_time(self, utc_stamp_str: str) -> datetime.datetime:
        """
        Resets expiration time one second earlier to account
        for any delays between expiration check and request for
        new token in session setting.

        Args:
            utcstamp: utc timestamp string

        Returns:
            UTC timestamp as `datetime.datetime` object
        """
        utcstamp = datetime.datetime.strptime(
            utc_stamp_str, "%Y-%m-%d %H:%M:%SZ"
        ) - datetime.timedelta(seconds=1)
        utcstamp = utcstamp.replace(tzinfo=datetime.timezone.utc)
        return utcstamp

    def _parse_server_response(self, response: requests.Response) -> None:
        """Parses authorization server response

        Raises:
            WorldcatAuthorizationError: If server returns an error code.
        """
        self.server_response = response
        if response.status_code == requests.codes.ok:
            self.token_str = response.json()["access_token"]
            self.token_expires_at = self._hasten_expiration_time(
                response.json()["expires_at"]
            )
            self.token_type = response.json()["token_type"]
        else:
            raise WorldcatAuthorizationError(response.content)

    def _payload(self) -> dict[str, str]:
        """Preps requests params"""
        return {
            "grant_type": self.grant_type,
            "scope": self.scopes,
        }

    def _post_token_request(self) -> requests.Response:
        """
        Fetches Worldcat access token for specified scope (web service)

        Returns:
            [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response)
            instance

        Raises:
            WorldcatAuthorizationError: If access token POST request encounters any errors.
        """  # noqa: E501

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

    def _token_headers(self) -> dict[str, str]:
        return {"User-Agent": self.agent, "Accept": "application/json"}

    def _token_url(self) -> str:
        return f"{self.oauth_server}/token"

    def is_expired(self) -> bool:
        """
        Checks if the access token is expired.

        Returns:
            bool: Whether or not the token is expired.

        Raises:
            TypeError:
                If `WorldcatAccessToken.token_expires_at` is not a
                `datetime.datetime` object.

        Example:
            ```py
            token = WorldcatAccessToken(
                key="my_WSKey_client_id",
                secret="my_WSKey_secret",
                scopes="WorldCatMetadataAPI",
                agent="my_app/1.0.0")
            print(token.is_expired())
            #>False
            ```
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
