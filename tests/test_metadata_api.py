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

    def test_URL_BASE(self, stub_session):
        assert stub_session.URL_BASE() == "https://metadata.api.oclc.org/worldcat"

    @pytest.mark.parametrize(
        "validationLevel",
        ["vaidateFull", "validateAdd", "validateReplace"],
    )
    def test_url_manage_bib_validate(self, validationLevel, stub_session):
        assert (
            stub_session._url_manage_bib_validate(validationLevel)
            == f"https://metadata.api.oclc.org/worldcat/manage/bibs/validate/{validationLevel}"
        )

    def test_url_manage_bib_current_oclc_number(self, stub_session):
        assert (
            stub_session._url_manage_bib_current_oclc_number()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/current"
        )

    def test_url_manage_bib_create(self, stub_session):
        assert (
            stub_session._url_manage_bib_create()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_manage_bib(self, oclcNumber, stub_session):
        assert (
            stub_session._url_manage_bib(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/manage/bibs/{oclcNumber}"
        )

    def test_url_manage_bib_match(self, stub_session):
        assert (
            stub_session._url_manage_bib_match()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/match"
        )

    def test_url_manage_ih_current(self, stub_session):
        assert (
            stub_session._url_manage_ih_current()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/current"
        )

    def test_url_manage_ih_set(self, stub_session):
        assert (
            stub_session._url_manage_ih_set()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/set"
        )

    def test_url_manage_ih_unset(self, stub_session):
        assert (
            stub_session._url_manage_ih_unset()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_manage_ih_oclc_number_set(self, oclcNumber, stub_session):
        assert (
            stub_session._url_manage_ih_oclc_number_set(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/manage/institution/holdings/{oclcNumber}/set"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_manage_ih_oclc_number_unset(self, oclcNumber, stub_session):
        assert (
            stub_session._url_manage_ih_oclc_number_unset(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/manage/institution/holdings/{oclcNumber}/unset"
        )

    def test_url_manage_ih_codes(self, stub_session):
        assert (
            stub_session._url_manage_ih_codes()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holding-codes"
        )

    def test_url_manage_lbd_create(self, stub_session):
        assert (
            stub_session._url_manage_lbd_create()
            == "https://metadata.api.oclc.org/worldcat/manage/lbds"
        )

    @pytest.mark.parametrize(
        "controlNumber",
        ["12345", 12345],
    )
    def test_url_manage_lbd(self, controlNumber, stub_session):
        assert (
            stub_session._url_manage_lbd(controlNumber)
            == f"https://metadata.api.oclc.org/worldcat/manage/lbds/{controlNumber}"
        )

    def test_url_manage_lhr_create(self, stub_session):
        assert (
            stub_session._url_manage_lhr_create()
            == "https://metadata.api.oclc.org/worldcat/manage/lhrs"
        )

    @pytest.mark.parametrize(
        "controlNumber",
        ["12345", 12345],
    )
    def test_url_manage_lhr(self, controlNumber, stub_session):
        assert (
            stub_session._url_manage_lhr(controlNumber)
            == f"https://metadata.api.oclc.org/worldcat/manage/lhrs/{controlNumber}"
        )

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

    def test_url_search_general_holdings_summary(self, stub_session):
        assert (
            stub_session._url_search_general_holdings_summary()
            == "https://metadata.api.oclc.org/worldcat/search/summary-holdings"
        )

    def test_url_search_brief_bibs(self, stub_session):
        assert (
            stub_session._url_search_brief_bibs()
            == "https://metadata.api.oclc.org/worldcat/search/brief-bibs"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_search_brief_bibs_oclc_number(self, oclcNumber, stub_session):
        assert (
            stub_session._url_search_brief_bibs_oclc_number(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/search/brief-bibs/{oclcNumber}"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_search_brief_bibs_other_editions(self, oclcNumber, stub_session):
        assert (
            stub_session._url_search_brief_bibs_other_editions(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/search/brief-bibs/{oclcNumber}/other-editions"
        )

    @pytest.mark.parametrize(
        "oclcNumber",
        ["850940461", "850940463", 850940467],
    )
    def test_url_search_classification_bibs(self, oclcNumber, stub_session):
        assert (
            stub_session._url_search_classification_bibs(oclcNumber)
            == f"https://metadata.api.oclc.org/worldcat/search/classification-bibs/{oclcNumber}"
        )

    def test_url_search_lhr_shared_print(self, stub_session):
        assert (
            stub_session._url_search_lhr_shared_print()
            == "https://metadata.api.oclc.org/worldcat/search/retained-holdings"
        )

    @pytest.mark.parametrize(
        "controlNumber",
        ["12345", 12345],
    )
    def test_url_search_lhr_control_number(self, controlNumber, stub_session):
        assert (
            stub_session._url_search_lhr_control_number(controlNumber)
            == f"https://metadata.api.oclc.org/worldcat/search/my-holdings/{controlNumber}"
        )

    def test_url_search_lhr(self, stub_session):
        assert (
            stub_session._url_search_lhr()
            == "https://metadata.api.oclc.org/worldcat/search/my-holdings"
        )

    def test_url_browse_lhr(self, stub_session):
        assert (
            stub_session._url_browse_lhr()
            == "https://metadata.api.oclc.org/worldcat/browse/my-holdings"
        )

    @pytest.mark.parametrize(
        "controlNumber",
        ["12345", 12345],
    )
    def test_url_search_lbd_control_number(self, controlNumber, stub_session):
        assert (
            stub_session._url_search_lbd_control_number(controlNumber)
            == f"https://metadata.api.oclc.org/worldcat/search/my-local-bib-data/{controlNumber}"
        )

    def test_url_search_lbd(self, stub_session):
        assert (
            stub_session._url_search_lbd()
            == "https://metadata.api.oclc.org/worldcat/search/my-local-bib-data"
        )

    @pytest.mark.http_code(200)
    def test_create_bib(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.create_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    def test_create_bib_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.create_bib(recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    def test_create_bib_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.create_bib(stub_marc_xml)
        assert "Argument 'recordFormat' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_get_bib_classification(self, stub_session, mock_session_response):
        assert stub_session.get_bib_classification(12345).status_code == 200

    def test_get_bib_classification_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_bib_classification()

    @pytest.mark.http_code(200)
    def test_get_bib_holdings(self, stub_session, mock_session_response):
        assert stub_session.get_bib_holdings(oclcNumber=12345).status_code == 200

    def test_get_bib_holdings_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_bib_holdings(holdingsAllVariantRecords=True)

    @pytest.mark.http_code(200)
    def test_get_brief_bib(self, stub_session, mock_session_response):
        assert stub_session.get_brief_bib(12345).status_code == 200

    def test_get_brief_bib_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_brief_bib()

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
    def test_get_current_oclc_number(self, stub_session, mock_session_response):
        assert (
            stub_session.get_current_oclc_number(
                oclcNumbers=["12345", "65891"]
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_get_full_bib(self, stub_session, mock_session_response):
        assert stub_session.get_full_bib(12345).status_code == 200

    @pytest.mark.http_code(200)
    def test_match_bib(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.match_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    def test_match_bib_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.match_bib(recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    def test_match_bib_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc21
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.match_bib(stub_marc21)
        assert "Argument 'recordFormat' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_replace_bib(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.replace_bib(
                "12345", stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_replace_bib_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.replace_bib("12345", recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_replace_bib_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.replace_bib("12345", stub_marc_xml)
        assert "Argument 'recordFormat' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_bib_holdings(self, stub_session, mock_session_response):
        assert stub_session.search_bib_holdings(oclcNumber=12345).status_code == 200

    def test_search_bib_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(TypeError) as exc:
            stub_session.search_bib_holdings(holdingsAllEditions=True)
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions(
        self, stub_session, mock_session_response
    ):
        assert stub_session.search_brief_bibs_other_editions(12345).status_code == 200

    @pytest.mark.http_code(200)
    def test_search_brief_bibs(self, stub_session, mock_session_response):
        assert stub_session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, stub_session, argm):
        with pytest.raises(TypeError) as exc:
            stub_session.search_brief_bibs(argm)
        assert "Argument 'q' is requried to construct query." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_shared_print_holdings(self, stub_session, mock_session_response):
        assert (
            stub_session.search_shared_print_holdings(oclcNumber=12345).status_code
            == 200
        )

    def test_search_shared_print_holdings_missing_query(
        self, stub_session, mock_session_response
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.search_shared_print_holdings()
        assert "One of the following args are required: oclcNumber, issn, isbn" in str(
            exc.value
        )

    @pytest.mark.http_code(200)
    def test_set_holding(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.set_holding(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    def test_set_holding_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.set_holding(recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    def test_set_holding_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.set_holding(stub_marc_xml)
        assert "Argument 'recordFormat' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_set_holding_oclc_number(self, stub_session, mock_session_response):
        assert stub_session.set_holding_oclc_number(850940548).status_code == 200

    def test_set_holding_oclc_number_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.set_holding_oclc_number()

    @pytest.mark.http_code(200)
    def test_unset_holding(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.unset_holding(
                record=stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    def test_unset_holding_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.unset_holding(recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    def test_unset_holding_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.unset_holding(stub_marc_xml)
        assert "Argument 'recordFormat' is missing." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_unset_holding_oclc_number(self, stub_session, mock_session_response):
        assert stub_session.unset_holding_oclc_number(850940548).status_code == 200

    def test_unset_holding_oclc_number_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.unset_holding_oclc_number()

    @pytest.mark.http_code(200)
    def test_validate_bib(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.validate_bib(
                stub_marc_xml,
                recordFormat="application/marcxml+xml",
                validationLevel="validateFull",
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_validate_bib_default(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        assert (
            stub_session.validate_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    def test_validate_bib_no_record_passed(self, stub_session):
        with pytest.raises(TypeError) as exc:
            stub_session.validate_bib(recordFormat="application/marcxml+xml")
        assert "Argument 'record' is missing." in str(exc.value)

    def test_validate_bib_no_recordFormat_passed(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(TypeError) as exc:
            stub_session.validate_bib(stub_marc_xml)
        assert "Argument 'recordFormat' is missing." in str(exc.value)


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
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
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
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )
        token.token_str = "invalid-token"
        err_msg = "401 Client Error: Unauthorized for url: https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045"
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": "Bearer invalid-token"})
            with pytest.raises(WorldcatRequestError) as exc:
                session.get_brief_bib(41266045)

            assert err_msg in str(exc.value)

    def test_get_brief_bib_with_stale_token(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )
        with MetadataSession(authorization=token) as session:
            session.authorization.is_expired() is False
            session.authorization.token_expires_at = datetime.datetime.now(
                datetime.timezone.utc
            ) - datetime.timedelta(0, 1)
            assert session.authorization.is_expired() is True
            response = session.get_brief_bib(oclcNumber=41266045)
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

    def test_get_bib_classification(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_bib_classification(41266045)

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/search/classification-bibs/41266045"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == [
                "dewey",
                "lc",
            ]

    @pytest.mark.holdings
    def test_get_bib_holdings(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_bib_holdings(41266045)

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/search/summary-holdings?oclcNumber=41266045"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == [
                "totalEditions",
                "totalHoldingCount",
                "totalSharedPrintCount",
            ]

    def test_get_current_oclc_number(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_current_oclc_number([41266045, "519740398"])

            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=41266045%2C519740398"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["controlNumbers"]
            assert sorted(jres["controlNumbers"][0].keys()) == ["current", "requested"]

    def test_get_current_oclc_number_str(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_current_oclc_number("41266045")

            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=41266045"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["controlNumbers"]
            assert sorted(jres["controlNumbers"][0].keys()) == ["current", "requested"]

    def test_get_full_bib(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_full_bib(41266045)

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/41266045"
            )
            assert response.status_code == 200

    @pytest.mark.holdings
    def test_get_institution_holding_codes(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holding_codes()

            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holding-codes"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == ["holdingLibraryCodes"]
            assert {"code": "Print Collection", "name": "NYPC"} in response.json()[
                "holdingLibraryCodes"
            ]

    @pytest.mark.holdings
    def test_get_institution_holdings(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holdings("982651100")

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
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holdings("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.unset_holding_oclc_number(850940548)

            response = session.set_holding_oclc_number(850940548)
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            response = session.unset_holding_oclc_number(850940548)
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/850940548/unset"
            )
            assert response.json()["action"] == "Unset Holdings"

    @pytest.mark.holdings
    def test_holding_set_unset_marcxml(self, live_keys, stub_marc_xml):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_institution_holdings("850940548")
            holdings = response.json()["holdings"]

            # make sure no holdings are set initially
            if len(holdings) > 0:
                response = session.unset_holding(
                    stub_marc_xml, recordFormat="application/marcxml+xml"
                )

            response = session.set_holding(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/set"
            )
            assert response.status_code == 200
            assert response.json()["action"] == "Set Holdings"

            response = session.unset_holding(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            )
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset"
            )
            assert response.json()["action"] == "Unset Holdings"

    def test_match_bib_marc21(self, live_keys, stub_marc21):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.match_bib(stub_marc21, recordFormat="application/marc")
            assert response.status_code == 200

    @pytest.mark.holdings
    def test_search_bib_holdings_oclc(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_bib_holdings(oclcNumber="41266045")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    @pytest.mark.holdings
    def test_search_bib_holdings_isbn(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_bib_holdings(isbn="9781597801744")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_search_brief_bibs(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bibs(
                "ti:zendegi AND au:egan",
                inLanguage="eng",
                inCatalogLanguage="eng",
                itemType="book",
                catalogSource="dlc",
                orderBy="mostWidelyHeld",
                limit=5,
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
            assert (
                response.request.url
                == "https://metadata.api.oclc.org/worldcat/search/brief-bibs?q=ti%3Azendegi+AND+au%3Aegan&inLanguage=eng&inCatalogLanguage=eng&catalogSource=dlc&itemType=book&orderBy=mostWidelyHeld&limit=5"
            )

    def test_search_brief_bibs_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bibs_other_editions(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_validate_bib(self, live_keys, stub_marc21):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.validate_bib(
                stub_marc21, recordFormat="application/marc"
            )
            assert response.status_code == 200
            assert (
                response.url
                == "https://metadata.api.oclc.org/worldcat/manage/bibs/validate/validateFull"
            )
