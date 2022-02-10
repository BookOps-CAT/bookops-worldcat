# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
import os

import pytest

from requests import Request

from bookops_worldcat.errors import WorldcatRequestError
from bookops_worldcat.query import Query
from bookops_worldcat.metadata_api import MetadataSession, WorldcatAccessToken


@pytest.mark.webtest
def test_live_query(live_keys):
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


@pytest.mark.http_code(404)
def test_http_error_query(stub_session, mock_session_response):
    header = {"Accept": "application/json"}
    url = (
        "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
    )
    req = Request("GET", url, headers=header, hooks=None)
    prepped = stub_session.prepare_request(req)

    with pytest.raises(WorldcatRequestError) as exc:
        query = Query(stub_session, prepped)

    assert "404 Client Error: 'foo' for url: https://foo.bar?query" in str(exc.value)


# @pytest.mark.http_code(200)
# def test_http_200_code_query(mock_token, mock_session_response):
#     with
