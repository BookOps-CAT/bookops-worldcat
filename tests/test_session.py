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

    def test_default_adapter(self, mock_token):
        with WorldcatSession(mock_token) as session:
            assert session.adapters["https://"].max_retries.total == 0

    def test_adapter_retries(self, mock_token):
        with WorldcatSession(
            authorization=mock_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[500, 502, 503, 504],
            allowedMethods=["GET", "POST", "PUT"],
        ) as session:
            assert session.adapters["https://"].max_retries.status_forcelist == [
                500,
                502,
                503,
                504,
            ]

    def test_no_statusForcelist(self, mock_token):
        with WorldcatSession(
            authorization=mock_token,
            totalRetries=2,
            backoffFactor=0.1,
            allowedMethods=["GET"],
        ) as session:
            assert session.adapters[
                "https://"
            ].max_retries.status_forcelist == frozenset({413, 429, 503})

    @pytest.mark.parametrize("arg", [[], "", 123, {}, ["123", "234"]])
    def test_statusForcelist_error(self, mock_token, arg):
        with pytest.raises(ValueError) as exc:
            WorldcatSession(
                authorization=mock_token,
                totalRetries=2,
                backoffFactor=0.1,
                statusForcelist=arg,
                allowedMethods=["GET"],
            )
        assert "Argument 'statusForcelist' must be a list of integers" in str(exc.value)
