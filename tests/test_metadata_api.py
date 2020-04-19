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
        assert session.base_url == "https://worldcat.org/bib"

    def test_session_header_on_init(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            assert session.headers == {
                "User-Agent": "bookops-worldcat/0.1.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept": 'application/atom+xml;content="application/vnd.oclc.marc21+xml"',
                "Connection": "keep-alive",
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
        mock_successful_session_request,
        oclc_no_arg,
        expectation,
    ):
        token = mock_token_initiation_via_credentials
        with MetadataSession(credentials=token) as session:
            with expectation:
                assert session.get_record(oclc_no_arg)

    def test_get_record_request(
        self, mock_token_initiation_via_credentials, mock_successful_session_request
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
