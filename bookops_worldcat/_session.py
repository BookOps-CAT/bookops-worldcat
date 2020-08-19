# -*- coding: utf-8 -*-

import requests

from . import __title__, __version__


class WorldcatSession(requests.Session):
    """Inherits all requests.Session methods"""

    def __init__(self):
        requests.Session.__init__(self)

        self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
