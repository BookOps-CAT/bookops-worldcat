# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self, credentials=None):
        requests.Session.__init__(self)

        if not credentials:
            raise AttributeError(
                "WorldcatSession requires WorldcatAccessToken object or WSkey."
            )

        self.timeout = (10, 10)
        self.headers.update({"User-Agent": f"{__title__}/{__version__}"})


class SearchSession(WorldcatSession):
    """ Worlcat Search API wrapper session. Inherits requests.Session methods"""

    def __init__(self, credentials=None):
        WorldcatSession.__init__(self, credentials)

        if type(credentials) is not str:
            raise TypeError("OCLC key (WSkey) can be only a string.")

        self.key = credentials
        self.base_url = "http://www.worldcat.org/webservices/catalog/"
        self.headers.update({"Accept": "application/xml"})
        self.payload = {"wskey": self.key}


class MetadataSession(WorldcatSession):
    """OCLC Metadata API wrapper session. Inherits requests.Session methods"""

    def __init__(self, credentials=None):
        WorldcatSession.__init__(self, credentials)

        if type(credentials).__name__ != "WorldcatAccessToken":
            raise TypeError("Invalid token object passed in the argument.")

        if credentials.token_str is None:
            raise TypeError(
                "Missing token_str in WorldcatAccessToken object passes as credentials."
            )

        self.base_url = "https://worldcat.org/"
