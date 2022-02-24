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
        "argm,expectation",
        [
            (123, pytest.raises(WorldcatSessionError)),
            ({}, pytest.raises(WorldcatSessionError)),
            ((), pytest.raises(WorldcatSessionError)),
        ],
    )
    def test_invalid_user_agent_arguments(self, argm, expectation, mock_token):
        with expectation:
            WorldcatSession(mock_token, agent=argm)
            assert "Argument 'agent' must be a str" in str(expectation.value)

    def test_default_timeout(self, mock_token):
        with WorldcatSession(mock_token, timeout=None) as session:
            assert session.timeout == (5, 5)

    def test_custom_timeout(self, mock_token):
        with WorldcatSession(mock_token, timeout=1) as session:
            assert session.timeout == 1
