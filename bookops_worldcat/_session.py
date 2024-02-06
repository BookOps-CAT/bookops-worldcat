# -*- coding: utf-8 -*-

"""
Base session class to allow extention of functionality to Worldcat Search API
and others.
"""

from typing import Optional, Tuple, Union

import requests

from . import __title__, __version__
from .authorize import WorldcatAccessToken
from .errors import WorldcatSessionError, WorldcatAuthorizationError


class WorldcatSession(requests.Session):
    """Base class, inherits all requests.Session methods"""

    def __init__(
        self,
        authorization: WorldcatAccessToken,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float]] = (
            5,
            5,
        ),
    ) -> None:
        """
        Args:
            authorization:          WorldcatAccessToken instance
            agent:                  "User-agent" parameter to attached to each
                                    request in the session
            timeout:                how long to wait for server to send data
                                    before giving up
        """
        super().__init__()

        self.authorization = authorization

        if not isinstance(self.authorization, WorldcatAccessToken):
            raise WorldcatSessionError(
                "Argument 'authorization' must be 'WorldcatAccessToken' object."
            )

        if agent is None:
            self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
        elif agent and isinstance(agent, str):
            self.headers.update({"User-Agent": agent})
        else:
            raise WorldcatSessionError("Argument 'agent' must be a string.")

        self.timeout = timeout

        self._update_authorization()

    def _get_new_access_token(self) -> None:
        """
        Allows to continue sending request with new access token after
        the previous one expired
        """
        try:
            self.authorization._request_token()
            self._update_authorization()
        except WorldcatAuthorizationError as exc:
            raise WorldcatSessionError(exc)

    def _update_authorization(self) -> None:
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})
