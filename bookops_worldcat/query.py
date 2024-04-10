# -*- coding: utf-8 -*-

"""
Handles actual requests to OCLC services
"""
from __future__ import annotations
from typing import Union, Tuple, TYPE_CHECKING
import sys

from requests.models import PreparedRequest
from requests.exceptions import ConnectionError, HTTPError, Timeout, RetryError
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
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            5,
            5,
        ),
    ) -> None:
        """Initializes Query object.

        Args:
            session:                `metadata_api.MetadataSession` instance
            prepared_request:       `requests.models.PreparedRequest` instance
            timeout:                how long to wait for server to send data before
                                    giving up; can accept different values for connect
                                    and read timeouts. default value is 5 seconds for
                                    read and 5 seconds for connect timeouts


        Raises:
            WorldcatRequestError: If the request encounters an error
        """
        if not isinstance(prepared_request, PreparedRequest):
            raise TypeError("Invalid type for argument 'prepared_request'.")

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
        except (Timeout, ConnectionError, RetryError):
            raise WorldcatRequestError(f"Connection Error: {sys.exc_info()[0]}")

        except Exception:
            raise WorldcatRequestError(f"Unexpected request error: {sys.exc_info()[0]}")
