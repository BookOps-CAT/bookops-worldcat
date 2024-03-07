# -*- coding: utf-8 -*-

import pytest


from bookops_worldcat._session import WorldcatSession
from bookops_worldcat.__version__ import __title__, __version__


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
        with pytest.raises(ValueError) as exc:
            WorldcatSession(mock_token, agent=arg)
        assert "Argument 'agent' must be a string." in str(exc.value)

    def test_default_timeout(self, mock_token):
        with WorldcatSession(mock_token) as session:
            assert session.timeout == (5, 5)

    def test_custom_timeout(self, mock_token):
        with WorldcatSession(mock_token, timeout=1) as session:
            assert session.timeout == 1

    def test_adapter_retry_total(self, mock_token):
        with WorldcatSession(mock_token) as session:
            assert session.adapters["https://"].max_retries.total == 3

    def test_adapter_force_list_pass(self, mock_token):
        with WorldcatSession(mock_token) as session:
            assert session.adapters["https://"].max_retries.status_forcelist == [
                406,
                429,
                500,
                502,
                503,
                504,
            ]
