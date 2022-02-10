# -*- coding: utf-8 -*-

"""
Handles actual requests to OCLC services
"""
import sys

from requests import Session
from requests.models import PreparedRequest
from requests.exceptions import ConnectionError, HTTPError, Timeout


from .errors import WorldcatRequestError


class Query:
    """
    Sends a request to OClC service and handles any exceptions
    received.
    """

    def __init__(
        self, session: Session, prepared_request: PreparedRequest, timeout: int
    ) -> None:
        self.request = prepared_request
        self.response = None

        self._send(session, timeout)

    def _send(self, session: Session, timeout: int) -> None:
        try:
            self.response = session.send(self.request, timeout=timeout)
            self.response.raise_for_status()
        except HTTPError as exc:
            raise WorldcatRequestError(f"{exc}")
        except (Timeout, ConnectionError):
            raise WorldcatRequestError(f"Connection error: {sys.exc_info()[0]}.")
        except:
            raise WorldcatRequestError(
                f"Unexpected request error: {sys.exc_info()[0]}."
            )
