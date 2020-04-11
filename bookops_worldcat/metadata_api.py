# -*- coding: utf-8 -*-

from ._session import WorldcatSession


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
