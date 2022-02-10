# -*- coding: utf-8 -*-

"""
Handles actual requests to OCLC services
"""
from typing import Optional, Union, Tuple
import sys

from requests import Session
from requests.models import PreparedRequest
from requests.exceptions import ConnectionError, HTTPError, Timeout


from .errors import WorldcatRequestError


class Query:
    """
    Sends a request to OClC service and unifies received excepitons
    """

    def __init__(
        self,
        session: Session,
        prepared_request: PreparedRequest,
        timeout: Optional[
            Union[int, float, Tuple[int, int], Tuple[float, float]]
        ] = None,
    ) -> None:
        """
        session:                        `requests.Session` instance
        prepared_request:               `requests.models.PreparedRequest` instance
        timeout:                        how long to wait for server to send data before
                                        giving up
        """
        self.response = None

        try:
            self.response = session.send(prepared_request, timeout=timeout)
            self.response.raise_for_status()
        except HTTPError as exc:
            raise WorldcatRequestError(f"{exc}")
        except (Timeout, ConnectionError):
            raise WorldcatRequestError(f"Connection error: {sys.exc_info()[0]}.")
        except:
            raise WorldcatRequestError(
                f"Unexpected request error: {sys.exc_info()[0]}."
            )
