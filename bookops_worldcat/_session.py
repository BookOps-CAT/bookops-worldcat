# -*- coding: utf-8 -*-

"""
Base session class to allow extention of functionality to Worldcat Search API
and others.
"""

from typing import Optional, Tuple, Union, List

import requests
from urllib3.util import Retry

from . import __title__, __version__
from .authorize import WorldcatAccessToken


class WorldcatSession(requests.Session):
    """Base class, inherits all requests.Session methods"""

    def __init__(
        self,
        authorization: WorldcatAccessToken,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            5,
            5,
        ),
        total_retries: int = 0,
        backoff_factor: float = 0,
        status_forcelist: Optional[List[int]] = [],
        allowed_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            authorization:          WorldcatAccessToken instance
            agent:                  "User-agent" parameter to attached to each
                                    request in the session
            timeout:                how long to wait for server to send data
                                    before giving up
            total_retries:          optional number of times to retry a request that
                                    failed or timed out. if total_retries argument is
                                    not passed, any arguments passed to
                                    backoff_factor, status_forcelist, and
                                    allowed_methods will be ignored. default is 0
            backoff_factor:         if total_retries is not 0, the backoff
                                    factor as a float to use to calculate amount of
                                    time session will sleep before attempting request
                                    again. default is 0
            status_forcelist:       if total_retries is not 0, a list of HTTP
                                    status codes to automatically retry requests on.
                                    if not specified, all failed requests will be
                                    retried up to number of total_retries.
                                    example: [500, 502, 503, 504]
            allowed_methods:        if total_retries is not 0, set of HTTP methods that
                                    requests should be retried on. if not specified,
                                    requests using any HTTP method verbs will be
                                    retried. example: ["GET", "POST"]
        """
        super().__init__()
        self.authorization = authorization

        if not isinstance(self.authorization, WorldcatAccessToken):
            raise TypeError(
                "Argument 'authorization' must be 'WorldcatAccessToken' object."
            )

        if agent is None:
            self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
        elif agent and isinstance(agent, str):
            self.headers.update({"User-Agent": agent})
        else:
            raise ValueError("Argument 'agent' must be a string.")

        self.timeout = timeout

        # if user provides retry args, create Retry object and mount adapter to session
        if total_retries != 0:
            retries = Retry(
                total=total_retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
                allowed_methods=allowed_methods,
            )
            self.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))

        self._update_authorization()

    def _get_new_access_token(self) -> None:
        """
        Allows to continue sending request with new access token after
        the previous one expired
        """
        self.authorization._request_token()
        self._update_authorization()

    def _update_authorization(self) -> None:
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})
