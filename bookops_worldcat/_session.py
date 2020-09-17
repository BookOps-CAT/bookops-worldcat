# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__
from bookops_worldcat.errors import WorldcatSessionError


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self, agent=None, timeout=None):
        requests.Session.__init__(self)

        if agent is None:
            self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
        elif type(agent) is str:
            self.headers.update({"User-Agent": agent})
        else:
            raise WorldcatSessionError("Argument 'agent' must be a str")

        self.timeout = timeout
        if not self.timeout:
            self.timeout = (3, 3)
