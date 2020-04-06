import pytest


from bookops_worldcat import __title__, __version__
from bookops_worldcat.session import WorldcatSession, SearchSession


class InvalidToken:
    def __init__(self):
        self.token_str = "fake_token_string"
        self.key = "fake_key"


class TestWorldcatSession:
    """Test base WorldcatSession used to derive basic functionality"""

    def test_missing_token_argument(self):
        with pytest.raises(AttributeError):
            assert WorldcatSession()

    def test_invalid_token_object_in_argument(self):
        token = InvalidToken()
        with pytest.raises(TypeError):
            assert WorldcatSession(token=token)

    def test_invalid_token_str_argument(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.token_str = None
        with pytest.raises(TypeError):
            assert WorldcatSession(token=token)

    def test_missing_token_key_argument(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.key = None
        with pytest.raises(TypeError):
            assert WorldcatSession(token=token)

    def test_WorldcatSession_default_timeout(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        assert WorldcatSession(token=token).timeout == (10, 10)

    def test_WorldcatSession_default_headers(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        session = WorldcatSession(token=token)
        assert "User-Agent" in session.headers
        assert session.headers["User-Agent"] == f"{__title__}/{__version__}"


class TestSearchSession:
    """Worldcat SearchSession tests"""

    def test_missing_token_argument(self):
        with pytest.raises(AttributeError):
            assert SearchSession()

    def test_invalid_token_type(self):
        token = InvalidToken()
        with pytest.raises(TypeError):
            assert SearchSession(token=token)

    def test_key_passed_from_token_credentials(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        session = SearchSession(token=token)
        assert session.key == "WSkey"

    def test_oclc_search_api_base_url(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        session = SearchSession(token=token)
        assert session.base_url == "http://www.worldcat.org/webservices/catalog/"

    def test_session_headers(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        session = SearchSession(token=token)
        assert "User-Agent" in session.headers
        assert session.headers["User-Agent"] == f"{__title__}/{__version__}"
        assert "Accept" in session.headers
        assert session.headers["Accept"] == "application/xml"

    def test_session_payload(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        session = SearchSession(token=token)
        assert session.payload == {"wskey": token.key}
