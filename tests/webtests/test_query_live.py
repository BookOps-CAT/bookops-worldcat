# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
import os

import pytest

from requests import Request

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
