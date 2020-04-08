import pytest
from requests.exceptions import ConnectionError, Timeout

from bookops_worldcat import __title__, __version__
from bookops_worldcat.session import WorldcatSession, SearchSession, MetadataSession


class InvalidToken:
    def __init__(self):
        self.token_str = "fake_token_string"
        self.key = "fake_key"


class MockConnectionError:
    def __init__(self, *args, **kwargs):
        raise ConnectionError


class MockTimeout:
    def __init__(self, *args, **kwargs):
        raise Timeout


class TestWorldcatSession:
    """Test base WorldcatSession used to derive basic functionality"""

    def test_missing_token_argument(self):
        with pytest.raises(AttributeError):
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


class TestSearchSession:
    """Worldcat SearchSession tests"""

    def test_missing_token_argument(self):
        with pytest.raises(AttributeError):
            assert SearchSession()

    def test_invalid_token_type(self):
        token = InvalidToken()
        with pytest.raises(TypeError):
            assert SearchSession(credentials=token)

    def test_missing_token_key_argument(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.key = None
        with pytest.raises(TypeError):
            assert SearchSession(credentials=token)

    def test_key_passed_from_token_credentials(
        self, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        with pytest.raises(TypeError):
            assert SearchSession(credentials=token)

    def test_oclc_search_api_base_url(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert session.base_url == "http://www.worldcat.org/webservices/catalog/"

    def test_session_headers(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert "User-Agent" in session.headers
        assert session.headers["User-Agent"] == f"{__title__}/{__version__}"
        assert "Accept" in session.headers
        assert session.headers["Accept"] == "application/xml"

    def test_session_payload(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert session.payload == {"wskey": key}

    def test_lookup_by_isbn_request(
        self, mock_credentials, mock_successful_search_api_lookup_isbn_request
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        results = session.lookup_by_isbn("12345")
        assert results.status_code == 200
        assert results.url == f"{session.base_url}content/isbn/12345"

    def test_lookup_by_isbn_connectionerror(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.lookup_by_isbn("12345")

    def test_lookup_by_isbn_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.lookup_by_isbn("12345")


class TestMetadataSession:
    """Worldcat MetadataSession tests"""

    def test_invalid_token_object_in_argument(self):
        token = InvalidToken()
        with pytest.raises(TypeError):
            assert MetadataSession(credentials=token)

    def test_invalid_token_str_argument(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.token_str = None
        with pytest.raises(TypeError):
            assert MetadataSession(credentials=token)

    def test_base_url(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        session = MetadataSession(credentials=token)
        assert session.base_url == "https://worldcat.org/"
