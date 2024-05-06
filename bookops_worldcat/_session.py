# -*- coding: utf-8 -*-

"""
Base session class to be subclassed for use with individual OCLC APIs.
"""

from typing import Optional, Tuple, Union, List

import requests
from urllib3.util import Retry

from . import __title__, __version__
from .authorize import WorldcatAccessToken


class WorldcatSession(requests.Session):
    """Base class for WorldCat API sessions. Inherits all `requests.Session` methods."""

    def __init__(
        self,
        authorization: WorldcatAccessToken,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            5,
            5,
        ),
        totalRetries: int = 0,
        backoffFactor: float = 0,
        statusForcelist: Optional[List[int]] = None,
        allowedMethods: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            authorization:
                `WorldcatAccessToken` instance.
            agent:
                `User-agent` parameter to attached to each request in the session.
            timeout:
                How long to wait for server to send data before giving up. Accepts
                separate values for connect and read timeouts or a single value.
            totalRetries:
                Optional number of times to retry a request that has failed or timed
                out. If `totalRetries` argument is not passed, all arguments passed
                to `backoffFactor`, `statusForcelist`, and `allowedMethods`
                will be ignored.
            backoffFactor:
                If `totalRetries` is not `0`, the backoff factor as a float to use to
                calculate amount of time session will sleep before attempting request
                again.
            statusForcelist:
                If `totalRetries` is not `0`, a list of HTTP status codes to
                automatically retry requests on. If not specified, failed requests with
                status codes 413, 429, and 503 will be retried up to number of
                `totalRetries`.

                **EXAMPLE:** `[500, 502, 503, 504]`
            allowedMethods:
                If `totalRetries` is not `0`, set of HTTP methods that requests should
                be retried on. If not specified, requests using any HTTP method verbs
                will be retried.

                **EXAMPLE:** `["GET", "POST"]`
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
        if totalRetries != 0:
            if statusForcelist is None:
                retries = Retry(
                    total=totalRetries,
                    backoff_factor=backoffFactor,
                    status_forcelist=Retry.RETRY_AFTER_STATUS_CODES,
                    allowed_methods=allowedMethods,
                )
            elif (
                isinstance(statusForcelist, List)
                and all(isinstance(x, int) for x in statusForcelist)
                and len(statusForcelist) > 0
            ):
                retries = Retry(
                    total=totalRetries,
                    backoff_factor=backoffFactor,
                    status_forcelist=statusForcelist,
                    allowed_methods=allowedMethods,
                )
            else:
                raise ValueError(
                    "Argument 'statusForcelist' must be a list of integers."
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
