# -*- coding: utf-8 -*-
import os

import pytest

from requests import Request

from bookops_worldcat.errors import WorldcatRequestError
from bookops_worldcat.query import Query
from bookops_worldcat.metadata_api import MetadataSession, WorldcatAccessToken


@pytest.mark.webtest
def test_temp(live_keys):
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

        query = Query(session, prepped, 2)
        print(query.response.status_code)
        print(query.response.url)
        print(query.response.request.headers)
        print(query.response.json())


@pytest.mark.http_code(404)
def test_temp2(mock_token, mock_session_response):
    with MetadataSession(authorization=mock_token) as session:
        header = {"Accept": "application/json"}
        url = "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
        req = Request(
            "GET",
            url,
            headers=header,
        )
        prepped = session.prepare_request(req)

        with pytest.raises(WorldcatRequestError) as exc:
            query = Query(session, prepped, 2)

        assert "404 Client Error: 'foo' for url: https://foo.bar?query" in str(
            exc.value
        )
