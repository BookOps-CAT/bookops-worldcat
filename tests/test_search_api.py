from contextlib import contextmanager

import pytest
from requests.exceptions import ConnectionError, Timeout


from bookops_worldcat import __title__, __version__
from bookops_worldcat import SearchSession


@contextmanager
def does_not_raise():
    yield


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


class TestSearchSession:
    """Worldcat SearchSession tests"""

    @pytest.mark.parametrize(
        "key,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("", pytest.raises(ValueError)),
            (InvalidToken(), pytest.raises(TypeError)),
            ("foo_bar", does_not_raise()),
        ],
    )
    def test_token_arguments(self, key, expectation):
        with expectation:
            SearchSession(credentials=key)

    def test_oclc_search_api_base_url(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert session.base_url == "http://www.worldcat.org/webservices/catalog"

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

    def test_prepare_request_payload(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        kwargs = {"key1": "val1", "key2": "val2", "key3": [], "key4": None}
        assert session._prepare_request_payload(**kwargs) == {
            "wskey": key,
            "key1": "val1",
            "key2": "val2",
        }

    def test_lookup_isbn_url(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert (
            session._lookup_isbn_url("12345")
            == "http://www.worldcat.org/webservices/catalog/content/isbn/12345"
        )

    def test_lookup_isbn_request(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        with SearchSession(credentials=key) as session:
            results = session.lookup_isbn("12345")
            assert results.status_code == 200

    @pytest.mark.parametrize(
        "keyword,level,expectation",
        [
            (None, "default", pytest.raises(TypeError)),
            (2, "default", pytest.raises(TypeError)),
            ("", "default", pytest.raises(ValueError)),
            ("1234x", "default", does_not_raise()),
            ("1234x", "full", does_not_raise()),
            ("1234x", None, pytest.raises(TypeError)),
            ("1234x", 2, pytest.raises(TypeError)),
            ("1234x", "", pytest.raises(ValueError)),
            ("1234x", "invalid_level", pytest.raises(ValueError)),
        ],
    )
    def test_lookup_isbn_arguments(
        self,
        mock_credentials,
        keyword,
        level,
        expectation,
        mock_successful_session_get_request,
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.lookup_isbn(isbn=keyword, service_level=level)

    def test_lookup_isbn_connectionerror(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.lookup_isbn("12345")

    def test_lookup_isbn_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.lookup_isbn("12345")

    def test_lookup_issn_url(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert (
            session._lookup_issn_url("1234-4567")
            == "http://www.worldcat.org/webservices/catalog/content/issn/1234-4567"
        )

    def test_lookup_issn_request(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        with SearchSession(credentials=key) as session:
            results = session.lookup_issn("1234-4567")
            assert results.status_code == 200

    @pytest.mark.parametrize(
        "keyword,input_service,expectation",
        [
            (None, "default", pytest.raises(TypeError)),
            (1234, "default", pytest.raises(TypeError)),
            ("", "default", pytest.raises(ValueError)),
            ("0000-1234", "default", does_not_raise()),
            ("0000-1234", "full", does_not_raise()),
            ("0000-1234", None, pytest.raises(TypeError)),
            ("0000-1234", 2, pytest.raises(TypeError)),
            ("0000-1234", "", pytest.raises(ValueError)),
            ("0000-1234", "invalid_level", pytest.raises(ValueError)),
        ],
    )
    def test_lookup_issn_arguments(
        self, mock_credentials, keyword, input_service, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.lookup_issn(issn=keyword, service_level=input_service)

    def test_lookup_issn_connectionerror(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.lookup_issn("1234-4567")

    def test_lookup_issn_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.lookup_issn("1234-4567")

    def test_lookup_oclc_number_url(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert (
            session._lookup_oclc_number_url("00012345")
            == "http://www.worldcat.org/webservices/catalog/content/00012345"
        )

    def test_lookup_oclc_number_request(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        with SearchSession(credentials=key) as session:
            results = session.lookup_oclc_number("00012345")
            assert results.status_code == 200

    @pytest.mark.parametrize(
        "keyword,input_service,expectation",
        [
            (None, "default", pytest.raises(TypeError)),
            ("ocn000123", "default", pytest.raises(ValueError)),
            ("", "default", pytest.raises(ValueError)),
            ("00012345", "default", does_not_raise()),
            (12345, "default", pytest.raises(TypeError)),
            ("0001234", "full", does_not_raise()),
            ("0001234", None, pytest.raises(TypeError)),
            ("0001234", "", pytest.raises(ValueError)),
            ("0001234", 2, pytest.raises(TypeError)),
        ],
    )
    def test_lookup_oclc_number_arguments(
        self, mock_credentials, keyword, input_service, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.lookup_oclc_number(oclc_number=keyword, service_level=input_service)

    def test_lookup_oclc_number_connectionerror(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.lookup_oclc_number("00012345")

    def test_lookup_oclc_number_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.lookup_oclc_number("00012345")

    def test_lookup_standard_number_url(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert (
            session._lookup_standard_number_url("00012345")
            == "http://www.worldcat.org/webservices/catalog/content/sn/00012345"
        )

    def test_lookup_standard_number_request(
        self, mock_credentials, mock_successful_session_get_request
    ):
        key = mock_credentials["key"]
        with SearchSession(credentials=key) as session:
            results = session.lookup_standard_number("00012345")
            assert results.status_code == 200

    @pytest.mark.parametrize(
        "input_keyword,input_level,expectation",
        [
            (None, "default", pytest.raises(TypeError)),
            (12345, "default", pytest.raises(TypeError)),
            ("", "default", pytest.raises(ValueError)),
            ("12345", "default", does_not_raise()),
            ("foo12345", "full", does_not_raise()),
            ("12345", "", pytest.raises(ValueError)),
            ("12345", None, pytest.raises(TypeError)),
            ("12345", 2, pytest.raises(TypeError)),
        ],
    )
    def test_lookup_standard_number_arguments(
        self, mock_credentials, input_keyword, input_level, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.lookup_standard_number(
                std_number=input_keyword, service_level=input_level
            )

    def test_lookup_standard_number_connectionerror(
        self, monkeypatch, mock_credentials
    ):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.lookup_standard_number("00012345")

    def test_lookup_standard_number_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.lookup_standard_number("00012345")

    def test_sru_query_url(self, mock_credentials):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        assert (
            session._sru_query_url('srw.kw="foo"')
            == 'http://www.worldcat.org/webservices/catalog/search/sru?query=srw.kw="foo"'
        )

    @pytest.mark.parametrize(
        "query_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("", pytest.raises(ValueError)),
            ('srw.kw="foo"', does_not_raise()),
            ('"foo"', pytest.raises(ValueError)),
            (12345, pytest.raises(TypeError)),
        ],
    )
    def test_sru_query_argument(self, mock_credentials, query_arg, expectation):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query=query_arg)

    @pytest.mark.parametrize(
        "start_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("1", pytest.raises(TypeError)),
            (0, pytest.raises(ValueError)),
            (-1, pytest.raises(ValueError)),
            (1, does_not_raise()),
            (1234, does_not_raise()),
        ],
    )
    def test_start_record_argument(self, mock_credentials, start_arg, expectation):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query='srw.kw="foo"', start_record=start_arg)

    @pytest.mark.parametrize(
        "max_rec,expectation",
        [
            (101, pytest.raises(ValueError)),
            (100, does_not_raise()),
            (50, does_not_raise()),
            (1, does_not_raise()),
            (0, pytest.raises(ValueError)),
            ("12", pytest.raises(TypeError)),
            (2.2, pytest.raises(TypeError)),
            (None, pytest.raises(TypeError)),
        ],
    )
    def test_sru_query_maximum_records(self, mock_credentials, max_rec, expectation):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query='srw.kw="foo"', maximum_records=max_rec)

    @pytest.mark.parametrize(
        "sort_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            (("foo", "bar"), pytest.raises(TypeError)),
            ([], pytest.raises(ValueError)),
            ([("score", "descending")], does_not_raise()),
            ([("relevance", "descending")], does_not_raise()),
            ([("relevance", "ascending")], pytest.raises(ValueError)),
            ([tuple(), ("relevance", "descending")], pytest.raises(ValueError)),
            (
                [("relevance", "descending"), ("library_count", "descending")],
                does_not_raise(),
            ),
            ([("relevance", "other_order")], pytest.raises(ValueError)),
            (["relevance", "descending"], pytest.raises(TypeError)),
            ([(None, "descending")], pytest.raises(TypeError)),
            ([("relevance", None)], pytest.raises(TypeError)),
            ([("", "descending")], pytest.raises(ValueError)),
            ([("relevance", "")], pytest.raises(ValueError)),
            ([("invalid_key", "descending")], pytest.raises(ValueError)),
            ([("relevance", "invalid_sort")], pytest.raises(ValueError)),
            ([("title", "ascending")], does_not_raise()),
            ([("author", "descending")], does_not_raise()),
            ([("date", "descending")], does_not_raise()),
            ([("library_count", "ascending")], does_not_raise()),
            ([("library_count", "descending")], does_not_raise()),
            ([("score", "ascending")], does_not_raise()),
        ],
    )
    def test_sru_query_sort_keys_argument_only(
        self, mock_credentials, sort_arg, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query='srw.kw="foo"', sort_keys=sort_arg)

    @pytest.mark.parametrize(
        "frbr_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("", pytest.raises(ValueError)),
            ("on", does_not_raise()),
            ("off", does_not_raise()),
        ],
    )
    def test_sru_query_frbr_grouping_alone(
        self, mock_credentials, frbr_arg, expectation
    ):
        """rely on correct default value of sort_keys argument"""
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query='srw.kw="foo"', frbr_grouping=frbr_arg)

    @pytest.mark.parametrize(
        "sort_arg,frbr_arg,expectation",
        [
            (
                [("title", "ascending"), ("date", "descending")],
                "on",
                pytest.raises(ValueError),
            ),
            ([("title", "ascending"), ("date", "descending")], "off", does_not_raise()),
        ],
    )
    def test_sru_query_sort_keys_and_frbr_grouping_combination(
        self, mock_credentials, sort_arg, frbr_arg, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(
                query='srw.kw="foo"', sort_keys=sort_arg, frbr_grouping=frbr_arg
            )

    @pytest.mark.parametrize(
        "srv_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("", pytest.raises(ValueError)),
            ("invalid_level", pytest.raises(ValueError)),
            ("default", does_not_raise()),
            ("full", does_not_raise()),
        ],
    )
    def test_sru_query_service_level_argument(
        self, mock_credentials, srv_arg, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            session.sru_query(query='srw.kw="foo"', service_level=srv_arg)

    @pytest.mark.parametrize(
        "sort_arg,returns,expectation",
        [
            ([("relevance", "ascending")], "relevance", does_not_raise()),
            ([("title", "ascending")], "Title", does_not_raise()),
            ([("author", "ascending")], "Author", does_not_raise()),
            ([("date", "ascending")], "Date", does_not_raise()),
            ([("library_count", "ascending")], "LibraryCount", does_not_raise()),
            ([("score", "ascending")], "Score", does_not_raise()),
            ([("relevance", "descending")], "relevance,,0", does_not_raise()),
            (
                [("score", "descending"), ("library_count", "descending")],
                "Score,,0 LibraryCount,,0",
                does_not_raise(),
            ),
            (
                [("title", "ascending"), ("date", "descending")],
                "Title Date,,0",
                does_not_raise(),
            ),
            (
                [
                    ("author", "ascending"),
                    ("title", "ascending"),
                    ("date", "descending"),
                ],
                "Author Title Date,,0",
                does_not_raise(),
            ),
        ],
    )
    def test_prepare_sort_keys(self, mock_credentials, sort_arg, returns, expectation):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            assert session._prepare_sort_keys(sort_arg) == returns

    @pytest.mark.parametrize(
        "query_arg,result,expectation",
        [
            (None, None, pytest.raises(TypeError)),
            ("", None, pytest.raises(ValueError)),
            ('kw="foo"', None, pytest.raises(ValueError)),
            ('srw.kw="foo"', 'srw.kw="foo"', does_not_raise()),
            (
                'srw.ti+=+"foo"+and+srw.su+all+"bar"',
                'srw.ti+=+"foo"+and+srw.su+all+"bar"',
                does_not_raise(),
            ),
            (
                'srw.ti+exact+"foo"+or+srw.ti+all+"bar"',
                'srw.ti+exact+"foo"+or+srw.ti+all+"bar"',
                does_not_raise(),
            ),
            (
                'srw.ti+=+"foo"+not+srw.au+=+"bar"',
                'srw.ti+=+"foo"+not+srw.au+=+"bar"',
                does_not_raise(),
            ),
            (
                'srw.au+all+"john smith"+(srw.su+=+"foo"+or+srw.su+all+"bar spam")',
                'srw.au+all+"john smith"+%28srw.su+=+"foo"+or+srw.su+all+"bar spam"%29',
                does_not_raise(),
            ),
        ],
    )
    def test_prepare_sru_query_str_exceptions(
        self, mock_credentials, query_arg, result, expectation
    ):
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with expectation:
            assert session._prepare_sru_query_str(query_arg) == result

    def test_sru_query_request_connectionerror(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(ConnectionError):
            session.sru_query(query='srw.kw="foo"')

    def test_sru_query_request_timeout(self, monkeypatch, mock_credentials):
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        key = mock_credentials["key"]
        session = SearchSession(credentials=key)
        with pytest.raises(Timeout):
            session.sru_query('srw.bn="00012345"')
