# -*- coding: utf-8 -*-

import pytest


from bookops_worldcat._session import WorldcatSession
from bookops_worldcat.__version__ import __title__, __version__
from bookops_worldcat.errors import WorldcatSessionError


class TestWorldcatSession:
    """Test the base WorldcatSession"""

    def test_default_user_agent_header(self, mock_token):
        assert (
            WorldcatSession(mock_token).headers["User-Agent"]
            == f"{__title__}/{__version__}"
        )

    def test_custom_user_agent_header(self, mock_token):
        assert (
            WorldcatSession(mock_token, agent="my_app").headers["User-Agent"]
            == "my_app"
        )

    @pytest.mark.parametrize(
        "arg",
        [123, {}, (), ""],
    )
    def test_invalid_user_agent_arguments(self, arg, mock_token):
        with pytest.raises(WorldcatSessionError) as exc:
            WorldcatSession(mock_token, agent=arg)
        assert "Argument 'agent' must be a string." in str(exc.value)

    def test_default_timeout(self, mock_token):
        with WorldcatSession(mock_token) as session:
            assert session.timeout == (5, 5)

    def test_custom_timeout(self, mock_token):
        with WorldcatSession(mock_token, timeout=1) as session:
            assert session.timeout == 1
