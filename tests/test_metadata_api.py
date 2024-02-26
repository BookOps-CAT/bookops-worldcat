# -*- coding: utf-8 -*-

from contextlib import contextmanager
import datetime
import os
from types import GeneratorType

import pytest


from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import (
    WorldcatRequestError,
    WorldcatAuthorizationError,
    InvalidOclcNumber,
)


@contextmanager
def does_not_raise():
    yield


class TestMockedMetadataSession:
    """Tests MetadataSession methods with mocking"""

    def test_base_session_initiation(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert type(session.authorization).__name__ == "WorldcatAccessToken"

            # test header set up correctly:
            assert (
                session.headers["Authorization"]
                == "Bearer tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
            )

    def test_missing_authorization(self):
        with pytest.raises(TypeError):
            MetadataSession()

    def test_invalid_authorizaiton(self):
        err_msg = "Argument 'authorization' must be 'WorldcatAccessToken' object."
        with pytest.raises(TypeError) as exc:
            MetadataSession(authorization="my_token")
        assert err_msg in str(exc.value)

    def test_get_new_access_token(self, mock_token, mock_now):
        assert mock_token.is_expired() is False
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.now(
                datetime.timezone.utc
            ) - datetime.timedelta(0, 1)
            assert session.authorization.is_expired() is True
            session._get_new_access_token()
            assert session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
            )
            assert session.authorization.is_expired() is False

    def test_get_new_access_token_exceptions(self, stub_session, mock_timeout):
        with pytest.raises(WorldcatAuthorizationError):
            stub_session._get_new_access_token()

    @pytest.mark.parametrize(
        "oclcNumbers,expectation",
        [
            pytest.param([], [], id="empty list"),
            pytest.param(["1", "2", "3"], ["1,2,3"], id="list of str"),
            pytest.param(["1"], ["1"], id="list of one"),
            pytest.param(["1"] * 50, [",".join(["1"] * 50)], id="full batch"),
            pytest.param(["1"] * 51, [",".join(["1"] * 50), "1"], id="2 batches"),
            pytest.param(
                ["1"] * 103,
                [",".join(["1"] * 50), ",".join(["1"] * 50), "1,1,1"],
                id="3 batches",
            ),
        ],
    )
    def test_split_into_legal_volume(self, stub_session, oclcNumbers, expectation):
        batches = stub_session._split_into_legal_volume(oclcNumbers)
        assert isinstance(batches, GeneratorType)
        all_batches = [b for b in batches]
        assert all_batches == expectation

    def test_url_base(self, stub_session):
        assert stub_session.BASE_URL == "https://metadata.api.oclc.org/worldcat"

    def test_url_search_shared_print_holdings(self, stub_session):
        assert (
            stub_session._url_search_shared_print_holdings()
            == "https://metadata.api.oclc.org/worldcat/search/bibs-retained-holdings"
        )

    def test_url_search_general_holdings(self, stub_session):
        assert (
            stub_session._url_search_general_holdings()
            == "https://metadata.api.oclc.org/worldcat/search/bibs-summary-holdings"
        )

    def test_url_search_brief_bibs(self, stub_session):
        assert (
            stub_session._url_search_brief_bibs()
            == "https://metadata.api.oclc.org/worldcat/search/brief-bibs"
        )

    @pytest.mark.parametrize(
        "argm",
        ["12345", 12345],
    )
    def test_url_search_brief_bibs_oclc_number(self, argm, stub_session):
        assert (
            stub_session._url_search_brief_bibs_oclc_number(oclcNumber=argm)
            == "https://metadata.api.oclc.org/worldcat/search/brief-bibs/12345"
        )

    def test_url_search_brief_bibs_other_editions(self, stub_session):
        assert (
            stub_session._url_search_brief_bibs_other_editions(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/search/brief-bibs/12345/other-editions"
        )

    def test_url_manage_bib(self, stub_session):
        assert (
            stub_session._url_manage_bibs(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/12345"
        )

    def test_url_manage_bib_current_oclc_number(self, stub_session):
        assert (
            stub_session._url_manage_bibs_current_oclc_number()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/current"
        )

    def test_url_manage_ih_set(self, stub_session):
        assert (
            stub_session._url_manage_ih_set(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/12345/set"
        )

    def test_url_manage_ih_unset(self, stub_session):
        assert (
            stub_session._url_manage_ih_unset(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/12345/unset"
        )

    def test_url_manage_ih_current(self, stub_session):
        assert (
            stub_session._url_manage_ih_current()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/current"
        )

    @pytest.mark.http_code(200)
    def test_get_brief_bib(self, stub_session, mock_session_response):
        assert stub_session.get_brief_bib(12345).status_code == 200

    def test_get_brief_bib_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_brief_bib()

    def test_get_brief_bib_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.get_brief_bib(oclcNumber=None)

    @pytest.mark.http_code(206)
    def test_get_brief_bib_odd_206_http_code(self, stub_session, mock_session_response):
        with does_not_raise():
            response = stub_session.get_brief_bib(12345)
        assert response.status_code == 206

    @pytest.mark.http_code(404)
    def test_get_brief_bib_404_error_response(
        self, stub_session, mock_session_response
    ):
        with pytest.raises(WorldcatRequestError) as exc:
            stub_session.get_brief_bib(12345)

        assert (
            "404 Client Error: 'foo' for url: https://foo.bar?query. Server response: spam"
            in (str(exc.value))
        )

    @pytest.mark.http_code(200)
    def test_get_full_bib(self, stub_session, mock_session_response):
        assert stub_session.get_full_bib(12345).status_code == 200

    def test_get_full_bib_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_full_bib()

    def test_get_full_bib_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.get_full_bib(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_get_institution_holdings(self, stub_session, mock_session_response):
        assert stub_session.get_institution_holdings("12345")[0].status_code == 200

    def test_get_institution_holdings_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_institution_holdings()

    def test_get_institution_holdings_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.get_institution_holdings(oclcNumbers=None)

    @pytest.mark.http_code(201)
    def test_holding_set(self, stub_session, mock_session_response):
        assert stub_session.holding_set(850940548).status_code == 201

    def test_holding_set_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holding_set()

    def test_holding_set_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.holding_set(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_holding_unset(self, stub_session, mock_session_response):
        assert stub_session.holding_unset(850940548).status_code == 200

    def test_holding_unset_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holding_unset()

    def test_holding_unset_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.holding_unset(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions(
        self, stub_session, mock_session_response
    ):
        assert stub_session.search_brief_bibs_other_editions(12345).status_code == 200

    def test_search_brief_bibs_other_editions_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_brief_bibs_other_editions("odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_brief_bibs(self, stub_session, mock_session_response):
        assert stub_session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, stub_session, argm):
        with pytest.raises(TypeError) as exc:
            stub_session.search_brief_bibs(argm)
        assert "Argument 'q' is requried to construct query." in str(exc.value)

    @pytest.mark.http_code(207)
    def test_get_current_oclc_number(self, stub_session, mock_session_response):
        assert (
            stub_session.get_current_oclc_number(
                oclcNumbers=["12345", "65891"]
            ).status_code
            == 207
        )

    @pytest.mark.http_code(207)
    def test_get_current_oclc_number_passed_as_str(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.get_current_oclc_number(oclcNumbers="12345,65891").status_code
            == 207
        )

    @pytest.mark.parametrize("argm", [(None), (""), ([])])
    def test_get_current_oclc_number_missing_numbers(self, stub_session, argm):
        err_msg = "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.get_current_oclc_number(argm)
        assert err_msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_bibs_holdings(self, stub_session, mock_session_response):
        assert stub_session.search_bibs_holdings(oclcNumber=12345).status_code == 200

    def test_search_bibs_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(TypeError) as exc:
            stub_session.search_bibs_holdings(holdingsAllEditions=True)
        assert msg in str(exc.value)

    def test_search_bibs_holdings_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_bibs_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_shared_print_holdings(self, stub_session, mock_session_response):
        assert (
            stub_session.search_shared_print_holdings(oclcNumber=12345).status_code
            == 200
        )

    def test_search_shared_print_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(TypeError) as exc:
            stub_session.search_shared_print_holdings(heldInState="NY")
        assert msg in str(exc.value)

    def test_search_shared_print_holdings_with_invalid_oclc_number_passsed(
        self, stub_session
    ):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_shared_print_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)


@pytest.mark.webtest
class TestLiveMetadataSession:
    """Runs rudimentary tests against live Metadata API"""

    def test_get_brief_bib_print_mat_request(self, live_keys):
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
            response = session.get_brief_bib(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_get_brief_bib_401_error(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        token.token_str = "invalid-token"
        err_msg = "401 Client Error: Unauthorized for url: https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045"
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": "Bearer invalid-token"})
            with pytest.raises(WorldcatRequestError) as exc:
                session.get_brief_bib(41266045)

            assert err_msg in str(exc.value)

    def test_get_full_bib(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_full_bib(41266045)

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/41266045"
            )
            assert response.status_code == 200

    def test_get_institution_holdings(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holdings("982651100")[0]

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
    def test_holding_set_unset(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holdings("850940548")[0]
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.holding_unset(850940548)

            response = session.holding_set(850940548)
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            # test deleting holdings
            response = session.holding_unset(850940548)
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset"
            )
            assert response.json()["action"] == "Unset Holdings"

    def test_brief_bibs_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bibs_other_editions(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_search_brief_bibs(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bibs(
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
                == "https://metadata.api.oclc.org/worldcat/search/brief-bibs?q=ti%3Azendegi+AND+au%3Aegan&inLanguage=eng&inCatalogLanguage=eng&catalogSource=dlc&itemType=book&itemSubType=book-printbook&itemSubType=book-digital&orderBy=mostWidelyHeld&limit=5"
            )

    def test_search_bibs_holdings(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_bibs_holdings(isbn="9781597801744")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_get_current_oclc_number(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_current_oclc_number([41266045, 519740398])

            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=41266045%2C519740398"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["controlNumbers"]
            assert sorted(jres["controlNumbers"][0].keys()) == ["current", "requested"]
