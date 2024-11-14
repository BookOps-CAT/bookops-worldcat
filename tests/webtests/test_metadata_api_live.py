# -*- coding: utf-8 -*-

import os
import pytest


from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import WorldcatRequestError


@pytest.mark.webtest
class TestLiveMetadataSession:
    """Runs tests against live Metadata API"""

    BRIEF_BIB_RESPONSE_KEYS = ["briefRecords", "numberOfRecords"]
    CAT_INFO_KEYS = [
        "catalogingAgency",
        "transcribingAgency",
        "catalogingLanguage",
        "levelOfCataloging",
    ]

    def test_bib_get(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get(850940461)
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            headers = response.headers
            assert endpoint == "worldcat/manage/bibs/850940461"
            assert response.status_code == 200
            assert headers["Content-Type"] == "application/marcxml+xml;charset=UTF-8"
            assert isinstance(response.content, bytes)
            assert response.content.decode().startswith("<?xml version=")

    def test_bib_get_classification(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_classification(850940461)
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert endpoint == "worldcat/search/classification-bibs/850940461"
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json;charset=UTF-8"
            assert sorted(response.json().keys()) == sorted(["dewey", "lc"])
            assert sorted(response.json()["dewey"].keys()) == ["mostPopular"]
            assert sorted(response.json()["lc"].keys()) == ["mostPopular"]

    def test_bib_get_current_oclc_number(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_current_oclc_number([41266045, 519740398])
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert (
                endpoint
                == "worldcat/manage/bibs/current?oclcNumbers=41266045%2C519740398"
            )
            assert sorted(response.json().keys()) == ["controlNumbers"]
            assert sorted(response.json()["controlNumbers"][0].keys()) == sorted(
                ["requested", "current"]
            )

    def test_bib_get_current_oclc_number_str(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_current_oclc_number("41266045")
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert endpoint == "worldcat/manage/bibs/current?oclcNumbers=41266045"
            assert sorted(response.json().keys()) == ["controlNumbers"]
            assert sorted(response.json()["controlNumbers"][0].keys()) == sorted(
                ["requested", "current"]
            )

    def test_bib_match(self, live_token, stub_marc_xml):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_match(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert endpoint == "worldcat/manage/bibs/match"
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json;charset=UTF-8"
            assert sorted(response.json().keys()) == sorted(
                self.BRIEF_BIB_RESPONSE_KEYS
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "edition",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                    "mergedOclcNumbers",
                    "issns",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)

    def test_bib_search(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_search(41266045)
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert endpoint == "worldcat/search/bibs/41266045"
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

    def test_bib_validate(self, live_token, stub_marc21):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_validate(
                stub_marc21, recordFormat="application/marc"
            )
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert endpoint == "worldcat/manage/bibs/validate/validateFull"
            assert response.headers["Content-Type"] == "application/json;charset=UTF-8"
            assert sorted(response.json().keys()) == sorted(["status", "httpStatus"])
            assert sorted(response.json()["status"].keys()) == sorted(
                ["description", "summary"]
            )

    def test_brief_bibs_get(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get(41266045)
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert endpoint == "worldcat/search/brief-bibs/41266045"
            assert response.status_code == 200
            assert "numberOfRecords" not in response.json().keys()
            assert sorted(response.json().keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "edition",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                    "mergedOclcNumbers",
                ]
            )
            assert sorted(response.json()["catalogingInfo"].keys()) == sorted(
                self.CAT_INFO_KEYS
            )

    def test_brief_bibs_search(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_search(
                q="ti:Zendegi", inLanguage="eng", inCatalogLanguage="eng"
            )
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert endpoint.split("?")[0] == "worldcat/search/brief-bibs"
            assert sorted(response.json().keys()) == sorted(
                ["briefRecords", "numberOfRecords"]
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "edition",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                    "mergedOclcNumbers",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)

    def test_brief_bibs_get_other_editions(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get_other_editions(41266045)
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert (
                endpoint.split("?")[0]
                == "worldcat/search/brief-bibs/41266045/other-editions"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == sorted(
                ["briefRecords", "numberOfRecords"]
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)

    def test_holdings_get_codes(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_codes()
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert endpoint == "worldcat/manage/institution/holding-codes"
            assert response.status_code == 200
            assert sorted(response.json().keys()) == ["holdingLibraryCodes"]
            assert all(
                sorted(list(i.keys())) == sorted(["code", "name"])
                for i in response.json()["holdingLibraryCodes"]
            )
            assert {"code": "Print Collection", "name": "NYPC"} in response.json()[
                "holdingLibraryCodes"
            ]

    def test_holdings_get_current(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_current("982651100")
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert (
                endpoint
                == "worldcat/manage/institution/holdings/current?oclcNumbers=982651100"
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
    def test_holdings_set_unset(self, live_token):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
            get_resp = session.holdings_get_current("850940548")
            holdings = get_resp.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset(850940548)

            set_resp = session.holdings_set(850940548)
            assert (
                set_resp.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert set_resp.status_code == 200
            assert set_resp.json()["action"] == "Set Holdings"

            # test deleting holdings
            unset_resp = session.holdings_unset(850940548)
            assert unset_resp.status_code == 200
            assert (
                unset_resp.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset?cascadeDelete=True"
            )
            assert unset_resp.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_cascadeDelete(self, live_token, stub_marc_xml):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
            get_resp = session.holdings_get_current("850940548")
            holdings = get_resp.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                session.holdings_unset(850940548)

            set_resp = session.holdings_set(850940548)
            assert (
                set_resp.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert set_resp.status_code == 200
            assert set_resp.json()["action"] == "Set Holdings"

            # test deleting holdings
            unset_resp = session.holdings_unset(850940548, cascadeDelete=False)
            assert unset_resp.status_code == 200
            assert (
                unset_resp.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset?cascadeDelete=False"
            )
            assert unset_resp.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_xml(self, live_token, stub_marc_xml):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
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
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset?cascadeDelete=True"
            )
            assert response.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holdings_set_unset_xml_cascadeDelete(self, live_token, stub_marc_xml):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
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
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset?cascadeDelete=False"
            )
            assert response.json()["action"] == "Unset Holdings"

    def test_shared_print_holdings_search(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.shared_print_holdings_search(oclcNumber="41266045")
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/search/bibs-retained-holdings?oclcNumber=41266045"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == sorted(
                ["briefRecords", "numberOfRecords"]
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "edition",
                    "institutionHolding",
                    "mergedOclcNumbers",
                    "language",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)

    def test_summary_holdings_get(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_get("41266045")
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/search/summary-holdings?oclcNumber=41266045&unit=M"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == sorted(
                ["totalEditions", "totalHoldingCount", "totalSharedPrintCount"]
            )

    def test_summary_holdings_search_isbn(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_search(isbn="9781597801744")
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert (
                endpoint
                == "worldcat/search/bibs-summary-holdings?isbn=9781597801744&preferredLanguage=eng&unit=M"
            )
            assert sorted(response.json().keys()) == sorted(
                self.BRIEF_BIB_RESPONSE_KEYS
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "edition",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                    "mergedOclcNumbers",
                    "institutionHolding",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)

    def test_summary_holdings_search_oclc(self, live_token):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_search(oclcNumber="41266045")
            endpoint = response.url.split("https://metadata.api.oclc.org/")[1]
            assert response.status_code == 200
            assert (
                endpoint
                == "worldcat/search/bibs-summary-holdings?oclcNumber=41266045&preferredLanguage=eng&unit=M"
            )
            assert sorted(response.json().keys()) == sorted(
                self.BRIEF_BIB_RESPONSE_KEYS
            )
            assert sorted(response.json()["briefRecords"][0].keys()) == sorted(
                [
                    "oclcNumber",
                    "title",
                    "creator",
                    "date",
                    "language",
                    "edition",
                    "publisher",
                    "isbns",
                    "publicationPlace",
                    "catalogingInfo",
                    "specificFormat",
                    "generalFormat",
                    "machineReadableDate",
                    "mergedOclcNumbers",
                    "institutionHolding",
                ]
            )
            assert sorted(
                response.json()["briefRecords"][0]["catalogingInfo"].keys()
            ) == sorted(self.CAT_INFO_KEYS)


@pytest.mark.webtest
@pytest.mark.usefixtures("live_keys")
class TestLiveMetadataSessionErrors:
    """Tests error responses from live Metadata API"""

    def test_errors_invalid_query_param(self):
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

    def test_errors_invalid_token(self):
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

    def test_errors_resource_not_found(self):
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

    def test_errors_unacceptable_header(self, stub_marc21):
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

    def test_error_max_retries(self, stub_marc21):
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
class TestAPISpec:
    """Compares API spec with MetadataSession methods"""

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

    def test_params_bib_get(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get)
            assert endpoint_args == method_args

    def test_params_bib_get_classification(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_classification(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get_classification)
            assert endpoint_args == method_args

    def test_params_bib_get_current_oclc_number(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.bib_get_current_oclc_number([41266045, 519740398])
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.bib_get_current_oclc_number)
            assert endpoint_args == method_args

    def test_params_bib_match_marcxml(
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

    def test_params_bib_validate(
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

    def test_params_brief_bibs_get(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_get)
            assert endpoint_args == method_args

    def test_params_brief_bibs_search(self, live_token, endpoint_params, method_params):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_search(
                q="ti:Zendegi", inLanguage="eng", inCatalogLanguage="eng"
            )
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_search)
            assert endpoint_args == method_args

    def test_params_brief_bibs_get_other_editions(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.brief_bibs_get_other_editions(41266045)
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.brief_bibs_get_other_editions)
            assert endpoint_args == method_args

    def test_params_holdings_get_codes(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_codes()
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.holdings_get_codes)
            assert endpoint_args == method_args

    def test_params_holdings_get_current(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.holdings_get_current("982651100")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.holdings_get_current)
            assert endpoint_args == method_args

    @pytest.mark.holdings
    def test_params_holdings_set_unset(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
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
    def test_params_holdings_set_unset_with_bib(
        self, live_token, endpoint_params, method_params, stub_marc_xml
    ):
        with MetadataSession(
            authorization=live_token,
            totalRetries=3,
            backoffFactor=0.5,
            statusForcelist=[408, 500, 502, 503, 504],
            allowedMethods=["GET", "POST"],
        ) as session:
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

    def test_params_shared_print_holdings_search(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.shared_print_holdings_search(oclcNumber="41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.shared_print_holdings_search)
            assert endpoint_args == method_args

    def test_params_summary_holdings_get(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_get("41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.summary_holdings_get)
            assert endpoint_args == method_args

    def test_params_summary_holdings_search_oclc(
        self, live_token, endpoint_params, method_params
    ):
        with MetadataSession(authorization=live_token) as session:
            response = session.summary_holdings_search(oclcNumber="41266045")
            endpoint_args = endpoint_params(
                response.request.url, response.request.method
            )
            method_args = method_params(session.summary_holdings_search)
            assert endpoint_args == method_args
