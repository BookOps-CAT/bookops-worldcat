import pytest


from bookops_worldcat import __title__, __version__
from bookops_worldcat._session import WorldcatSession


class TestWorldcatSession:
    """Test base WorldcatSession used to derive basic functionality"""

    def test_missing_token_argument(self):
        with pytest.raises(TypeError):
            assert WorldcatSession()

    def test_WorldcatSession_default_timeout(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        assert WorldcatSession(credentials=token).timeout == (10, 10)

    def test_WorldcatSession_default_headers(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        session = WorldcatSession(credentials=token)
        assert "User-Agent" in session.headers
        assert session.headers["User-Agent"] == f"{__title__}/{__version__}"
