# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self, credentials=None):
        requests.Session.__init__(self)

        if credentials is None:
            raise TypeError(
                "WorldcatSession credential argument requires ' \
                'WorldcatAccessToken instance or WSkey."
            )

        self.timeout = (10, 10)
        self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
