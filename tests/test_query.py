# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
import datetime
import os

import pytest

from requests import Request

from bookops_worldcat.errors import WorldcatRequestError
from bookops_worldcat.query import Query
from bookops_worldcat.metadata_api import MetadataSession, WorldcatAccessToken


@pytest.mark.webtest
def test_query_live(live_keys):
    token = WorldcatAccessToken(
        key=os.getenv("WCKey"),
        secret=os.getenv("WCSecret"),
        scopes=os.getenv("WCScopes"),
    )
    with MetadataSession(authorization=token) as session:
        header = {"Accept": "application/json"}
        url = "https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045"
        req = Request(
            "GET",
            url,
            headers=header,
        )
        prepped = session.prepare_request(req)

        with does_not_raise():
            query = Query(session, prepped, timeout=5)

        assert query.response.status_code == 200


def test_query_not_prepared_request(stub_session):
    with pytest.raises(TypeError) as exc:
        req = Request("GET", "https://foo.org")
        Query(stub_session, req, timeout=2)
    assert "Invalid type for argument 'prepared_request'." in str(exc.value)


@pytest.mark.http_code(200)
def test_query_with_stale_token(stub_session, mock_now, mock_session_response):
    stub_session.authorization.token_expires_at = datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.timedelta(0, 1)
    assert stub_session.authorization.is_expired() is True

    req = Request("GET", "http://foo.org")
    prepped = stub_session.prepare_request(req)
    query = Query(stub_session, prepped)
    assert stub_session.authorization.is_expired() is False
    assert query.response.status_code == 200


@pytest.mark.http_code(200)
def test_query_http_200_response(stub_session, mock_session_response):
    with does_not_raise():
        req = Request("GET", "https://foo.org")
        prepped = stub_session.prepare_request(req)
        query = Query(stub_session, prepped)
        assert query.response.status_code == 200


@pytest.mark.http_code(201)
def test_query_http_201_response(stub_session, mock_session_response):
    with does_not_raise():
        req = Request("GET", "https://foo.org")
        prepped = stub_session.prepare_request(req)
        query = Query(stub_session, prepped)
        assert query.response.status_code == 201


@pytest.mark.http_code(206)
def test_query_http_206_response(stub_session, mock_session_response):
    with does_not_raise():
        req = Request("GET", "https://foo.org")
        prepped = stub_session.prepare_request(req)
        query = Query(stub_session, prepped)
        assert query.response.status_code == 206


@pytest.mark.http_code(207)
def test_query_http_207_response(stub_session, mock_session_response):
    with does_not_raise():
        req = Request("GET", "https://foo.org")
        prepped = stub_session.prepare_request(req)
        query = Query(stub_session, prepped)
        assert query.response.status_code == 207


@pytest.mark.http_code(404)
def test_query_http_404_response(stub_session, mock_session_response):
    header = {"Accept": "application/json"}
    url = "https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045"
    req = Request("GET", url, headers=header, hooks=None)
    prepped = stub_session.prepare_request(req)

    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert (
        "404 Client Error: 'foo' for url: https://foo.bar?query. Server response: spam"
        in str(exc.value)
    )


@pytest.mark.http_code(500)
def test_query_http_500_response(stub_session, mock_session_response):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert (
        "500 Server Error: 'foo' for url: https://foo.bar?query. Server response: spam"
        in str(exc.value)
    )


def test_query_timeout_exception(stub_session, mock_timeout):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "Connection Error: <class 'requests.exceptions.Timeout'>" in str(exc.value)


def test_query_connection_exception(stub_session, mock_connection_error):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "Connection Error: <class 'requests.exceptions.ConnectionError'>" in str(
        exc.value
    )


def test_query_retry_exception(stub_session, mock_retry_error):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "Connection Error: <class 'requests.exceptions.RetryError'>" in str(
        exc.value
    )


def test_query_unexpected_exception(stub_session, mock_unexpected_error):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "Unexpected request error: <class 'Exception'>" in str(exc.value)


def test_query_timeout_retry(stub_retry_session, caplog):
    req = Request("GET", "https://foo.org")
    prepped = stub_retry_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError):
        Query(stub_retry_session, prepped)

    assert "Retry(total=0, " in caplog.records[2].message
    assert "Retry(total=1, " in caplog.records[1].message
    assert "Retry(total=2, " in caplog.records[0].message
