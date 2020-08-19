# -*- coding: utf-8 -*-


from bookops_worldcat._session import WorldcatSession
from bookops_worldcat.__version__ import __title__, __version__


class TestWorldcatSession:
    """Test the base WorldcatSession"""

    def test_default_user_agent_header(self):
        assert WorldcatSession().headers["User-Agent"] == f"{__title__}/{__version__}"
