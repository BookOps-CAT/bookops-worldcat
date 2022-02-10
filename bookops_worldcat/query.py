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

    `Query.response` attribute is `requests.Response` instance that
    can be parsed to exctract received information from the web service.
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
        Args:
            session:                        `requests.Session` instance
            prepared_request:               `requests.models.PreparedRequest` instance
            timeout:                        how long to wait for server to send data
                                            before giving up

        Raises:
            WorldcatRequestError

        """
        if not isinstance(prepared_request, PreparedRequest):
            raise AttributeError("Invalid type for argument 'prepared_request'.")

        self.response = None

        try:
            self.response = session.send(prepared_request, timeout=timeout)

            if "/ih/data" in prepared_request.url:
                if self.response.status_code == 409:
                    # HTTP 409 code returns when trying to set/unset
                    # holdings on already set/unset record
                    # It is reasonable not to raise any exceptions
                    # in this case
                    pass  # pragma: no cover
                else:
                    self.response.raise_for_status()
            else:
                self.response.raise_for_status()

        except HTTPError as exc:
            raise WorldcatRequestError(f"{exc}")
        except (Timeout, ConnectionError):
            raise WorldcatRequestError(f"Connection Error: {sys.exc_info()[0]}")
        except:
            raise WorldcatRequestError(f"Unexpected request error: {sys.exc_info()[0]}")
