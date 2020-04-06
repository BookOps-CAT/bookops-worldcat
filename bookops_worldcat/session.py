# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self, token=None):
        requests.Session.__init__(self)

        if not token:
            raise AttributeError("WorldcatSession requires WorldcatAccessToken object.")

        if type(token).__name__ != "WorldcatAccessToken":
            raise TypeError("Invalid token object passed in the argument.")

        if token.token_str is None or token.key is None:
            raise TypeError("Invalid token object.")

        self.timeout = (10, 10)
        self.headers.update({"User-Agent": f"{__title__}/{__version__}"})


class SearchSession(WorldcatSession):
    def __init__(self, token=None):
        WorldcatSession.__init__(self, token)
        self.base_url = "http://www.worldcat.org/webservices/catalog/"
        self.key = token.key
        self.headers.update({"Accept": "application/xml"})
        self.payload = {"wskey": self.key}
