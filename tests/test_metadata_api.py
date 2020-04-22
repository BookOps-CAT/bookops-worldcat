# -*- coding: utf-8 -*-

from contextlib import contextmanager

import pytest
from requests.exceptions import ConnectionError, Timeout


from bookops_worldcat import MetadataSession


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
        assert session.base_url == "https://worldcat.org"

    def test_session_header_on_init(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert session.headers == {
                "User-Agent": "bookops-worldcat/0.1.0",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Accept": "*/*",
                "Authorization": "Bearer tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW",
            }

    @pytest.mark.parametrize(
        "oclc_no_arg,expectation",
        [
            ("000000001", "https://worldcat.org/bib/data/000000001"),
            (211111111, "https://worldcat.org/bib/data/211111111"),
        ],
    )
    def test_get_record_url(
        self, mock_token_initiation_via_credentials, oclc_no_arg, expectation
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert session._get_record_url(oclc_no_arg) == expectation

    @pytest.mark.parametrize(
        "oclc_nos,buckets,expectation",
        [
            ([], 0, [],),
            (["1", "2", "3"], 1, ["1,2,3"]),
            ([1, 2, 3], 1, ["1,2,3"]),
            (["1"], 1, ["1"]),
            (["1"] * 50, 1, [",".join(["1"] * 50)]),
            (["1"] * 51, 2, [",".join(["1"] * 50), "1"]),
            (["1"] * 103, 3, [",".join(["1"] * 50), ",".join(["1"] * 50), "1,1,1"]),
        ],
    )
    def test_split_into_legal_volume(
        self, mock_token_initiation_via_credentials, oclc_nos, buckets, expectation
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert session._split_into_legal_volume(oclc_nos) == expectation

    @pytest.mark.parametrize(
        "oclc_no_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("ocn123456790", pytest.raises(ValueError)),
            ("2111111111", does_not_raise()),
            (2111111111, pytest.raises(TypeError)),
        ],
    )
    def test_verify_oclc_number(
        self, mock_token_initiation_via_credentials, oclc_no_arg, expectation,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                assert session._verify_oclc_number(oclc_no_arg)

    @pytest.mark.parametrize(
        "oclc_no_arg,expectation",
        [
            (None, pytest.raises(TypeError)),
            ("ocn123456790", pytest.raises(ValueError)),
            ("2111111111", does_not_raise()),
        ],
    )
    def test_get_record_oclc_number_argument_exceptions(
        self,
        mock_token_initiation_via_credentials,
        mock_successful_session_get_request,
        oclc_no_arg,
        expectation,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                assert session.get_record(oclc_no_arg)

    def test_get_record_request(
        self, mock_token_initiation_via_credentials, mock_successful_session_get_request
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            response = session.get_record("211111111")
            assert response.status_code == 200

    def test_get_record_request_connectionerror(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        session = MetadataSession(credentials=token)
        with pytest.raises(ConnectionError):
            session.get_record("211111111")

    def test_get_record_request_timeout(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        session = MetadataSession(credentials=token)
        with pytest.raises(Timeout):
            session.get_record("211111111")

    def test_holdings_status_url(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert (
                session._holdings_status_url()
                == "https://worldcat.org/ih/checkholdings"
            )

    @pytest.mark.parametrize(
        "res_arg,returns,expectation",
        [
            (None, "application/atom+json", does_not_raise()),
            (2, None, pytest.raises(ValueError)),
            ("foo", None, pytest.raises(ValueError)),
            ("xml", "application/atom+xml", does_not_raise()),
            ("json", "application/atom+json", does_not_raise()),
        ],
    )
    def test_verify_holdings_response_argument(
        self, mock_token_initiation_via_credentials, res_arg, returns, expectation
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                assert session._verify_holdings_response_argument(res_arg) == returns

    @pytest.mark.parametrize(
        "oclc_no_arg,res_arg,expectation",
        [
            (None, "xml", pytest.raises(TypeError)),
            (2111111111, "xml", pytest.raises(TypeError)),
            ("ocn2111111111", "json", pytest.raises(ValueError)),
            ("2111111111", "other", pytest.raises(ValueError)),
            ("2111111111", None, does_not_raise()),
            ("2111111111", "xml", does_not_raise()),
            ("2111111111", "json", does_not_raise()),
        ],
    )
    def test_holdings_get_status(
        self,
        mock_token_initiation_via_credentials,
        mock_successful_session_get_request,
        oclc_no_arg,
        res_arg,
        expectation,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                session.holdings_get_status(
                    oclc_number=oclc_no_arg, response_format=res_arg,
                )

    def test_holdings_get_status_request(
        self, mock_token_initiation_via_credentials, mock_successful_session_get_request
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            response = session.holdings_get_status(oclc_number="211111111")
            assert response.status_code == 200

    def test_holdings_get_status_request_connectionerror(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.get", MockConnectionError)
        session = MetadataSession(credentials=token)
        with pytest.raises(ConnectionError):
            session.holdings_get_status("211111111")

    def test_holdings_get_status_request_timeout(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.get", MockTimeout)
        session = MetadataSession(credentials=token)
        with pytest.raises(Timeout):
            session.holdings_get_status("211111111")

    def test_holdings_set_url(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert session._holdings_set_url() == "https://worldcat.org/ih/data"

    def test_holdings_set_request_connectionerror(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.post", MockConnectionError)
        session = MetadataSession(credentials=token)
        with pytest.raises(ConnectionError):
            session.holdings_set("211111111")

    def test_holdings_set_request_timeout(
        self, monkeypatch, mock_token_initiation_via_credentials
    ):
        token = mock_token_initiation_via_credentials
        monkeypatch.setattr("requests.Session.post", MockTimeout)
        session = MetadataSession(credentials=token)
        with pytest.raises(Timeout):
            session.holdings_set("211111111")

    @pytest.mark.parametrize(
        "oclc_no_arg,res_arg,expectation",
        [
            (None, "xml", pytest.raises(TypeError)),
            (2111111111, "xml", pytest.raises(TypeError)),
            ("ocn2111111111", "json", pytest.raises(ValueError)),
            ("2111111111", "other", pytest.raises(ValueError)),
            ("2111111111", None, does_not_raise()),
            ("2111111111", "xml", does_not_raise()),
            ("2111111111", "json", does_not_raise()),
        ],
    )
    def test_holdings_set(
        self,
        mock_token_initiation_via_credentials,
        mock_successful_session_post_request,
        oclc_no_arg,
        res_arg,
        expectation,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                session.holdings_set(
                    oclc_number=oclc_no_arg, response_format=res_arg,
                )

    def test_holdings_set_request(
        self,
        mock_token_initiation_via_credentials,
        mock_successful_session_post_request,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            response = session.holdings_set(oclc_number="211111111")
            assert response.status_code == 200
