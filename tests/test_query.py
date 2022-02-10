# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
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
        principal_id=os.getenv("WCPrincipalID"),
        principal_idns=os.getenv("WCPrincipalIDNS"),
    )
    with MetadataSession(authorization=token) as session:
        header = {"Accept": "application/json"}
        url = "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
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
    with pytest.raises(AttributeError) as exc:
        req = Request("GET", "https://foo.org")
        Query(stub_session, req, timeout=2)
    assert "Invalid type for argument 'prepared_request'." in str(exc.value)


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
    url = (
        "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
    )
    req = Request("GET", url, headers=header, hooks=None)
    prepped = stub_session.prepare_request(req)

    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "404 Client Error: 'foo' for url: https://foo.bar?query" in str(exc.value)


@pytest.mark.http_code(500)
def test_query_http_500_response(stub_session, mock_session_response):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "500 Server Error: 'foo' for url: https://foo.bar?query" in str(exc.value)


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


def test_query_unexpected_exception(stub_session, mock_unexpected_error):
    req = Request("GET", "https://foo.org")
    prepped = stub_session.prepare_request(req)
    with pytest.raises(WorldcatRequestError) as exc:
        Query(stub_session, prepped)

    assert "Unexpected request error: <class 'Exception'>" in str(exc.value)


@pytest.mark.http_code(409)
def test_query_holding_endpoint_409_http_code(stub_session, mock_session_response):
    req = Request("POST", "https://worldcat.org/ih/data", params={"foo": "bar"})
    prepped = stub_session.prepare_request(req)
    with does_not_raise():
        query = Query(stub_session, prepped)

    assert query.response.status_code == 409
