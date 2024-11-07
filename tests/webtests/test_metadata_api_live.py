# -*- coding: utf-8 -*-

import os
import pytest


from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import WorldcatRequestError


@pytest.mark.webtest
@pytest.mark.usefixtures("live_keys")
class TestLiveMetadataSession:
    """Runs tests against live Metadata API"""

    BRIEF_BIB_RESPONSE_KEYS = ["briefRecords", "numberOfRecords"]
    CAT_INFO_KEYS = [
        "catalogingAgency",
        "transcribingAgency",
        "catalogingLanguage",
        "levelOfCataloging",
    ]

    def test_bib_get_response(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get(850940461)
            endpoint = response.url.strip("https://metadata.api.oclc.org/")
            headers = response.headers
            assert endpoint == "worldcat/manage/bibs/850940461"
            assert response.status_code == 200
            assert headers["Content-Type"] == "application/marcxml+xml;charset=UTF-8"
            assert isinstance(response.content, bytes)
            assert response.content.decode().startswith("<?xml version=")

    def test_bib_get_classification_response(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_classification(850940461)
            endpoint = response.url.strip("https://metadata.api.oclc.org/")
            assert endpoint == "worldcat/search/classification-bibs/850940461"
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json;charset=UTF-8"
            assert sorted(response.json().keys()) == sorted(["dewey", "lc"])
            assert sorted(response.json()["dewey"].keys()) == ["mostPopular"]
            assert sorted(response.json()["lc"].keys()) == ["mostPopular"]

    def test_bib_get_current_oclc_number(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.bib_get_current_oclc_number([41266045, 519740398])

            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=41266045%2C519740398"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["controlNumbers"]
            assert sorted(jres["controlNumbers"][0].keys()) == ["current", "requested"]

    def test_bib_get_current_oclc_number_str(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.bib_get_current_oclc_number("41266045")

            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=41266045"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["controlNumbers"]
            assert sorted(jres["controlNumbers"][0].keys()) == ["current", "requested"]

    def test_bib_match_marcxml(self, live_keys, stub_marc_xml):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.bib_match(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == sorted(
                ["numberOfRecords", "briefRecords"]
            )

    def test_bib_search(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        with MetadataSession(authorization=token) as session:
            response = session.bib_search(41266045)
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/search/bibs/41266045"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == sorted(
                [
                    "identifier",
                    "title",
                    "contributor",
                    "subjects",
                    "classification",
                    "publishers",
                    "date",
                    "language",
                    "edition",
                    "note",
                    "format",
                    "description",
                    "related",
                    "work",
                    "editionCluster",
                    "database",
                    "digitalAccessAndLocations",
                ]
            )

    def test_bib_validate(self, live_keys, stub_marc21):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.bib_validate(
                stub_marc21, recordFormat="application/marc"
            )
            assert response.status_code == 200
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/validate/validateFull"
            )
            assert sorted(response.json().keys()) == sorted(["httpStatus", "status"])

    def test_brief_bibs_get(self, live_keys):
        fields = sorted(
            [
                "catalogingInfo",
                "creator",
                "date",
                "edition",
                "generalFormat",
                "isbns",
                "language",
                "machineReadableDate",
                "mergedOclcNumbers",
                "oclcNumber",
                "publicationPlace",
                "publisher",
                "specificFormat",
                "title",
            ]
        )

        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.brief_bibs_get(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_brief_bibs_search(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.brief_bibs_search(
                "ti:zendegi AND au:egan",
                inLanguage="eng",
                inCatalogLanguage="eng",
                itemType="book",
                itemSubType=["book-printbook", "book-digital"],
                catalogSource="dlc",
                orderBy="mostWidelyHeld",
                limit=5,
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/search/brief-bibs?q=ti%3Azendegi+AND+au%3Aegan&inLanguage=eng&inCatalogLanguage=eng&catalogSource=dlc&itemType=book&itemSubType=book-printbook&itemSubType=book-digital&retentionCommitments=False&groupRelatedEditions=False&groupVariantRecords=False&preferredLanguage=eng&showHoldingsIndicators=False&unit=M&orderBy=mostWidelyHeld&offset=1&limit=5"
            )

    def test_brief_bibs_get_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.brief_bibs_get_other_editions(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_holdings_get_current(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_current("982651100")

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/current?oclcNumbers=982651100"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == ["holdings"]
            assert sorted(response.json()["holdings"][0].keys()) == sorted(
                [
                    "requestedControlNumber",
                    "currentControlNumber",
                    "institutionSymbol",
                    "holdingSet",
                ]
            )

    @pytest.mark.holdings
    def test_holdings_set_unset(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_current("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.holdings_unset(850940548)

            response = session.holdings_set(850940548)
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            # test deleting holdings
            response = session.holdings_unset(850940548)
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset?cascadeDelete=True"
            )
            assert response.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_cascadeDelete_False(self, live_keys, stub_marc_xml):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_current("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.holdings_unset(850940548)

            response = session.holdings_set(850940548)
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            # test deleting holdings
            response = session.holdings_unset(850940548, cascadeDelete=False)
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset?cascadeDelete=False"
            )
            assert response.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_marcxml(self, live_keys, stub_marc_xml):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_current("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.holdings_unset_with_bib(
                    stub_marc_xml, recordFormat="application/marcxml+xml"
                )

            response = session.holdings_set_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            response = session.holdings_unset_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset?cascadeDelete=True"
            )
            assert response.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_marcxml_cascadeDelete_False(
        self, live_keys, stub_marc_xml
    ):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_current("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.holdings_unset_with_bib(
                    stub_marc_xml, recordFormat="application/marcxml+xml"
                )

            response = session.holdings_set_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            # test deleting holdings
            response = session.holdings_unset_with_bib(
                stub_marc_xml,
                recordFormat="application/marcxml+xml",
                cascadeDelete=False,
            )
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset?cascadeDelete=False"
            )
            assert response.json()["action"] == "Unset Holdings"

    def test_holdings_get_codes(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_get_codes()

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holding-codes"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == ["holdingLibraryCodes"]
            assert {"code": "Print Collection", "name": "NYPC"} in response.json()[
                "holdingLibraryCodes"
            ]

    def test_summary_holdings_search_oclc(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.summary_holdings_search(oclcNumber="41266045")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_summary_holdings_search_isbn(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.summary_holdings_search(isbn="9781597801744")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields


@pytest.mark.webtest
@pytest.mark.usefixtures("live_keys")
class TestLiveMetadataSessionErrors:
    """Tests error responses from live Metadata API"""

    def test_400_invalid_query_param(self):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        with MetadataSession(authorization=token) as session:
            with pytest.raises(WorldcatRequestError) as exc:
                session.brief_bibs_get(-41266045)
            assert (
                '400 Client Error:  for url: https://metadata.api.oclc.org/worldcat/search/brief-bibs/-41266045. Server response: {"type":"INVALID_QUERY_PARAMETER_VALUE","title":"Validation Failure","detail":"oclcNumber must be a positive whole number","invalid-params":[{"reason":"Invalid Value: -41266045"}]}'
                == str(exc.value)
            )

    def test_401_invalid_token_error(self):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        token.token_str = "invalid-token"
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": "Bearer invalid-token"})
            with pytest.raises(WorldcatRequestError) as exc:
                session.brief_bibs_get(41266045)

            assert (
                '401 Client Error: Unauthorized for url: https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045. Server response: {"message":"Unauthorized"}'
                == str(exc.value)
            )

    def test_404_failed_resource_not_found(self):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        with MetadataSession(authorization=token) as session:
            with pytest.raises(WorldcatRequestError) as exc:
                session.lbd_get(12345)
            assert (
                '404 Client Error:  for url: https://metadata.api.oclc.org/worldcat/manage/lbds/12345. Server response: {"type":"NOT_FOUND","title":"Unable to perform the lbd read operation.","detail":{"summary":"NOT_FOUND","description":"Not able to find the requested LBD"}}'
                == str(exc.value)
            )

    def test_406_unacceptable_header_error(self, stub_marc21):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            with pytest.raises(WorldcatRequestError) as exc:
                session.bib_validate(stub_marc21, recordFormat="foo/bar")
            assert (
                '406 Client Error:  for url: https://metadata.api.oclc.org/worldcat/manage/bibs/validate/validateFull. Server response: {"type":"NOT_ACCEPTABLE","title":"Invalid \'Content-Type\' header.","detail":"A request with an invalid \'Content-Type\' header was attempted: foo/bar"}'
                == (str(exc.value))
            )
            assert session.adapters["https://"].max_retries.total == 0

    def test_retry_error(self, stub_marc21):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(
            authorization=token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[406],
            allowedMethods=["GET", "POST"],
        ) as session:
            with pytest.raises(WorldcatRequestError) as exc:
                session.bib_validate(stub_marc21, recordFormat="foo/bar")
            assert "Connection Error: <class 'requests.exceptions.RetryError'>" in (
                str(exc.value)
            )
            assert session.adapters["https://"].max_retries.total == 3


@pytest.mark.webtest
@pytest.mark.usefixtures("live_keys")
class TestLiveMetadataSessionParams:
    """
    Runs tests against live Metadata API and tests checks that params in `MetadataSession` methods match expected values from YAML file.
    """

    def test_open_api_spec_check(self, metadata_session_open_api_spec):
        """Confirm API spec contains the same endpoints as expected."""
        endpoints = metadata_session_open_api_spec["paths"]
        assert len(endpoints) == 29
        assert sorted(endpoints) == sorted(
            [
                "/worldcat/manage/bibs/validate/{validationLevel}",
                "/worldcat/manage/bibs/current",
                "/worldcat/manage/bibs",
                "/worldcat/manage/bibs/{oclcNumber}",
                "/worldcat/manage/bibs/match",
                "/worldcat/manage/institution/holdings/current",
                "/worldcat/manage/institution/holdings/{oclcNumber}/set",
                "/worldcat/manage/institution/holdings/{oclcNumber}/unset",
                "/worldcat/manage/institution/holdings/set",
                "/worldcat/manage/institution/holdings/unset",
                "/worldcat/manage/institution/holding-codes",
                "/worldcat/manage/lbds/{controlNumber}",
                "/worldcat/manage/lbds",
                "/worldcat/manage/lhrs/{controlNumber}",
                "/worldcat/manage/lhrs",
                "/worldcat/search/brief-bibs",
                "/worldcat/search/brief-bibs/{oclcNumber}",
                "/worldcat/search/classification-bibs/{oclcNumber}",
                "/worldcat/search/brief-bibs/{oclcNumber}/other-editions",
                "/worldcat/search/bibs-retained-holdings",
                "/worldcat/search/bibs-summary-holdings",
                "/worldcat/search/bibs/{oclcNumber}",
                "/worldcat/search/summary-holdings",
                "/worldcat/search/retained-holdings",
                "/worldcat/search/my-local-bib-data/{controlNumber}",
                "/worldcat/search/my-local-bib-data",
                "/worldcat/search/my-holdings/{controlNumber}",
                "/worldcat/search/my-holdings",
                "/worldcat/browse/my-holdings",
            ]
        )
        post_endpoints = [
            "/worldcat/manage/bibs/validate/{validationLevel}",
            "/worldcat/manage/bibs",
            "/worldcat/manage/bibs/match",
            "/worldcat/manage/institution/holdings/{oclcNumber}/set",
            "/worldcat/manage/institution/holdings/{oclcNumber}/unset",
            "/worldcat/manage/institution/holdings/set",
            "/worldcat/manage/institution/holdings/unset",
            "/worldcat/manage/lbds",
            "/worldcat/manage/lhrs",
        ]
        get_endpoints = [
            "/worldcat/manage/bibs/current",
            "/worldcat/manage/institution/holdings/current",
            "/worldcat/manage/institution/holding-codes",
            "/worldcat/search/brief-bibs",
            "/worldcat/search/brief-bibs/{oclcNumber}",
            "/worldcat/search/classification-bibs/{oclcNumber}",
            "/worldcat/search/brief-bibs/{oclcNumber}/other-editions",
            "/worldcat/search/bibs-retained-holdings",
            "/worldcat/search/bibs-summary-holdings",
            "/worldcat/search/bibs/{oclcNumber}",
            "/worldcat/search/summary-holdings",
            "/worldcat/search/retained-holdings",
            "/worldcat/search/my-local-bib-data/{controlNumber}",
            "/worldcat/search/my-local-bib-data",
            "/worldcat/search/my-holdings/{controlNumber}",
            "/worldcat/search/my-holdings",
            "/worldcat/browse/my-holdings",
        ]
        for endpoint in endpoints:
            methods = list(endpoints[endpoint].keys())
            if endpoint in post_endpoints:
                assert methods == ["post"]
            elif endpoint in get_endpoints:
                assert methods == ["get"]
            elif endpoint == "/worldcat/manage/bibs/{oclcNumber}":
                assert sorted(methods) == ["get", "put"]
            else:
                assert sorted(methods) == ["delete", "get", "put"]

    def test_bib_get(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get)
            assert endpoint_args == method_args

    def test_bib_get_classification(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_classification(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get_classification)
            assert endpoint_args == method_args

    def test_bib_get_current_oclc_number(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_current_oclc_number([41266045, 519740398])
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get_current_oclc_number)
            assert endpoint_args == method_args

    def test_bib_match_marcxml(
        self, live_token, stub_marc_xml, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_match(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_match)
            assert endpoint_args == method_args

    def test_bib_validate(
        self, live_token, stub_marc21, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_validate(
                stub_marc21, recordFormat="application/marc"
            )
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_validate)
            assert endpoint_args == method_args

    def test_brief_bibs_get(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_get)
            assert endpoint_args == method_args

    def test_brief_bibs_search(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_search(
                q="ti:Zendegi", inLanguage="eng", inCatalogLanguage="eng"
            )
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_search)
            assert endpoint_args == method_args

    def test_brief_bibs_get_other_editions(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get_other_editions(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_get_other_editions)
            assert endpoint_args == method_args

    def test_holdings_get_codes(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_codes()
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.holdings_get_codes)
            assert endpoint_args == method_args

    def test_holdings_get_current(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_current("982651100")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.holdings_get_current)
            assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_holdings_set_unset(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            get_response = session.holdings_get_current("850940548")
            holdings = get_response.json()["holdings"]
            current_holding_endpoint_args = endpoint_params(
                get_response.request.url, get_response.request.method
            )
            current_holding_method_args = method_params(session.holdings_get_current)
            assert current_holding_endpoint_args == current_holding_method_args

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset(850940548)

            # test setting holdings
            set_response = session.holdings_set(850940548)
            set_holding_endpoint_args = endpoint_params(
                set_response.request.url, set_response.request.method
            )
            set_holding_method_args = method_params(session.holdings_set)
            assert set_holding_endpoint_args == set_holding_method_args

            # test deleting holdings
            unset_response = session.holdings_unset(oclcNumber=850940548)
            unset_holding_endpoint_args = endpoint_params(
                unset_response.request.url, unset_response.request.method
            )
            unset_holding_method_args = method_params(session.holdings_unset)
            assert unset_holding_endpoint_args == unset_holding_method_args

    @pytest.mark.holdings
    def test_holdings_set_unset_with_bib(
        self, live_token, endpoint_params, method_params, stub_marc_xml
    ):
        with MetadataSession(authorization=live_token) as session:
            get_response = session.holdings_get_current("850940548")
            holdings = get_response.json()["holdings"]
            current_holding_endpoint_args = endpoint_params(
                get_response.request.url, get_response.request.method
            )
            current_holding_method_args = method_params(session.holdings_get_current)
            assert current_holding_endpoint_args == current_holding_method_args

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset_with_bib(
                    stub_marc_xml, recordFormat="application/marcxml+xml"
                )

            # test setting holdings
            set_response = session.holdings_set_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            set_holding_endpoint_args = endpoint_params(
                set_response.request.url, set_response.request.method
            )
            set_holding_method_args = method_params(session.holdings_set_with_bib)
            assert set_holding_endpoint_args == set_holding_method_args

            # test deleting holdings
            unset_response = session.holdings_unset_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            unset_holding_endpoint_args = endpoint_params(
                unset_response.request.url, unset_response.request.method
            )
            unset_holding_method_args = method_params(session.holdings_unset_with_bib)
            assert unset_holding_endpoint_args == unset_holding_method_args

    def test_shared_print_holdings_search(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.shared_print_holdings_search(oclcNumber="41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.shared_print_holdings_search)
            assert endpoint_args == method_args

    def test_summary_holdings_get(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_get("41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.summary_holdings_get)
            assert endpoint_args == method_args

    def test_summary_holdings_search_oclc(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_search(oclcNumber="41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.summary_holdings_search)
            assert endpoint_args == method_args
