# -*- coding: utf-8 -*-

"""
Handles actual requests to OCLC services
"""
from __future__ import annotations
from typing import Optional, Union, Tuple, TYPE_CHECKING
import sys

from requests.models import PreparedRequest
from requests.exceptions import ConnectionError, HTTPError, Timeout
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from .errors import WorldcatRequestError


if TYPE_CHECKING:
    from .metadata_api import MetadataSession  # pragma: no cover


class Query:
    """
    Sends a request to OCLC service and unifies exceptions.
    Query object handles refreshing expired token before request is
    made to the web service.

    `Query.response` attribute is `requests.Response` instance that
    can be parsed to extract information received from the web service.
    """

    def __init__(
        self,
        session: MetadataSession,
        prepared_request: PreparedRequest,
        timeout: Optional[
            Union[int, float, Tuple[int, int], Tuple[float, float]]
        ] = None,
    ) -> None:
        """
        Args:
            session:                        `metadata_api.MetadataSession` instance
            prepared_request:               `requests.models.PreparedRequest` instance
            timeout:                        how long to wait for server to send data
                                            before giving up

        Raises:
            WorldcatRequestError

        """
        if not isinstance(prepared_request, PreparedRequest):
            raise TypeError("Invalid type for argument 'prepared_request'.")

        # allow session to retry a request up to 3 times
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        # make sure access token is still valid and if not request a new one
        if session.authorization.is_expired():
            session._get_new_access_token()

        try:
            self.response = session.send(prepared_request, timeout=timeout)
            self.response.raise_for_status()

        except HTTPError as exc:
            raise WorldcatRequestError(
                f"{exc}. Server response: "  # type: ignore
                f"{self.response.content.decode('utf-8')}"
            )
        except (Timeout, ConnectionError):
            raise WorldcatRequestError(f"Connection Error: {sys.exc_info()[0]}")

        except Exception:
            raise WorldcatRequestError(f"Unexpected request error: {sys.exc_info()[0]}")
