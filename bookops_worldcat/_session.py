# -*- coding: utf-8 -*-

"""
Base session class to allow extention of functionality to Worldcat Search API
and others.
"""

from typing import Tuple, Union

import requests

from . import __title__, __version__
from bookops_worldcat.errors import WorldcatSessionError


class WorldcatSession(requests.Session):
    """Base class, inherits all requests.Session methods"""

    def __init__(
        self,
        agent: str = None,
        timeout: Union[int, float, Tuple[float, float], Tuple[int, int]] = None,
    ) -> None:
        requests.Session.__init__(self)

        if agent is None:
            self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
        elif type(agent) is str:
            self.headers.update({"User-Agent": agent})
        else:
            raise WorldcatSessionError("Argument 'agent' must be a str")

        if timeout is None:
            self.timeout = (3, 3)
        else:
            self.timeout = timeout
