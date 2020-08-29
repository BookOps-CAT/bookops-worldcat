# -*- coding: utf-8 -*-

import pytest


from bookops_worldcat._session import WorldcatSession
from bookops_worldcat.__version__ import __title__, __version__


class TestWorldcatSession:
    """Test the base WorldcatSession"""

    def test_default_user_agent_header(self):
        assert WorldcatSession().headers["User-Agent"] == f"{__title__}/{__version__}"

    def test_custom_user_agent_header(self):
        assert WorldcatSession(agent="my_app").headers["User-Agent"] == "my_app"

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (123, pytest.raises(TypeError)),
            ({}, pytest.raises(TypeError)),
            ((), pytest.raises(TypeError)),
        ],
    )
    def test_invalid_user_agent_arguments(self, argm, expectation):
        with expectation:
            WorldcatSession(agent=argm)
            assert "Argument 'agent' must be a str" in str(expectation.value)

    def test_default_timeout(self):
        with WorldcatSession() as session:
            assert session.timeout == (3, 3)
