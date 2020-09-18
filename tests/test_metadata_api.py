# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os

import pytest
import requests

from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import WorldcatSessionError, InvalidOclcNumber


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

    def test_invalid_credentials(self):
        with pytest.raises(WorldcatSessionError) as exc:
            MetadataSession()
            assert (
                "Argument 'authorization' must include 'WorldcatAccessToken' obj."
                in str(exc.value)
            )

    def test_get_new_access_token(self, mock_token):
        assert mock_token.is_expired() is False
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            session._get_new_access_token()
            assert mock_token.is_expired() is False

    def test_get_new_access_token_exceptions(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session._get_new_access_token()

    def test_url_base(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert session._url_base() == "https://worldcat.org"

    def test_url_search_base(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_search_base()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1"
            )

    def test_url_shared_print_holdings(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_member_shared_print_holdings()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/bibs-retained-holdings"
            )

    def test_url_member_general_holdings(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_member_general_holdings()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/bibs-summary-holdings"
            )

    def test_url_brief_bib_search(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_search()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs"
            )

    @pytest.mark.parametrize(
        "argm, expectation",
        [
            (
                "12345",
                "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345",
            ),
            (
                12345,
                "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345",
            ),
        ],
    )
    def test_url_brief_bib_oclc_number(self, argm, expectation, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_oclc_number(oclcNumber=argm)
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345"
            )

    def test_url_brief_bib_other_editions(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_other_editions(oclcNumber="12345")
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345/other-editions"
            )

    def test_url_lhr_control_number(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_lhr_control_number(controlNumber="12345")
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/my-holdings/12345"
            )

    def test_url_lhr_search(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_lhr_search()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/my-holdings"
            )

    def test_url_lhr_shared_print(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_lhr_shared_print()
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/retained-holdings"
            )

    def test_url_bib_oclc_number(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_oclc_number(oclcNumber="12345")
                == "https://worldcat.org/bib/data/12345"
            )

    def test_url_bib_check_oclc_numbers(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_check_oclc_numbers()
                == "https://worldcat.org/bib/checkcontrolnumbers"
            )

    def test_url_bib_holding_libraries(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_holding_libraries()
                == "https://worldcat.org/bib/holdinglibraries"
            )

    def test_url_bib_holdings_action(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert session._url_bib_holdings_action() == "https://worldcat.org/ih/data"

    def test_url_bib_holdings_check(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_holdings_check()
                == "https://worldcat.org/ih/checkholdings"
            )

    def test_url_bib_holdings_batch_action(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_holdings_batch_action()
                == "https://worldcat.org/ih/datalist"
            )

    def test_url_bib_holdings_multi_institution_batch_action(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_bib_holdings_multi_institution_batch_action()
                == "https://worldcat.org/ih/institutionlist"
            )

    def test_get_brief_bib(self, mock_token, mock_successful_session_get_request):
        with MetadataSession(authorization=mock_token) as session:
            assert session.get_brief_bib(12345).status_code == 200

    def test_get_brief_bib_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_brief_bib()

    def test_get_brief_bib_with_stale_token(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            response = session.get_brief_bib(oclcNumber=12345)
            assert mock_token.is_expired() is False
            assert response.status_code == 200

    def test_get_brief_bib_timout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_brief_bib(12345)

    def test_get_brief_bib_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_brief_bib(12345)

    def test_get_brief_bib_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_brief_bib(12345)

    def test_get_brief_bib_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.get_brief_bib(12345)
                assert msg in str(exc.value)

    def test_search_brief_bib_other_editions(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_brief_bib_other_editions(12345).status_code == 200

    def test_search_brief_bibs_other_editions_stale_token(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            response = session.search_brief_bib_other_editions(12345)
            assert mock_token.is_expired() is False
            assert response.status_code == 200

    def test_search_brief_bib_other_editions_timout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bib_other_editions(12345)

    def test_search_brief_bib_other_editions_connectionerror(
        self, mock_token, mock_connectionerror
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bib_other_editions(12345)

    def test_search_brief_bib_other_editions_unexpected_error(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bib_other_editions(12345)

    def test_search_brief_bibs_other_editions_invalid_oclc_number(self, mock_token):
        msg = "Invalid OCLC # was passed as an argument"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_brief_bib_other_editions("odn12345")
                assert msg in str(exc.value)

    def test_search_brief_bib_other_editions_400_error_response(
        self, mock_token, mock_400_response
    ):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_brief_bib_other_editions(oclcNumber=12345)
                assert msg in str(exc.value)

    def test_seach_brief_bibs(self, mock_token, mock_successful_session_get_request):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, mock_token, argm):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_brief_bibs(argm)
                assert "Argument 'q' is requried to construct query." in str(exc.value)

    def test_search_brief_bibs_with_stale_token(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            response = session.search_brief_bibs(q="ti:foo")
            assert mock_token.is_expired() is False
            assert response.status_code == 200

    def test_search_brief_bibs_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bibs("ti:foo")

    def test_search_brief_bibs_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bibs("ti:foo")

    def test_search_brief_bibs_unexpected_error(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_brief_bibs("ti:foo")

    def test_search_brief_bibs_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_brief_bibs("ti:foo")
                assert msg in str(exc.value)

    def test_search_shared_print_holdings(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session.search_shared_print_holdings(oclcNumber=12345).status_code
                == 200
            )

    def test_search_shared_print_holdings_missing_arguments(self, mock_token):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_shared_print_holdings(heldInState="NY", limit=20)
                assert msg in str(exc.value)

    def test_search_shared_print_holdings_with_invalid_oclc_number_passsed(
        self, mock_token
    ):
        msg = "Invalid OCLC # was passed as an argument"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_shared_print_holdings(oclcNumber="odn12345")
                assert msg in str(exc.value)

    def test_search_shared_print_holdings_with_stale_token(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            response = session.search_shared_print_holdings(oclcNumber=12345)
            assert mock_token.is_expired() is False
            assert response.status_code == 200

    def test_search_shared_print_holdings_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_shared_print_holdings(oclcNumber="12345")

    def test_search_shared_print_holdings_connectionerror(
        self, mock_token, mock_connectionerror
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_shared_print_holdings(oclcNumber=12345)

    def test_search_shared_print_holdings_unexpectederror(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_shared_print_holdings(oclcNumber="12345")

    def test_search_shared_print_holdings_400_error_response(
        self, mock_token, mock_400_response
    ):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_shared_print_holdings(oclcNumber=12345)
                assert msg in str(exc.value)

    def test_search_general_holdings(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_general_holdings(oclcNumber=12345).status_code == 200

    def test_search_general_holdings_missing_arguments(self, mock_token):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_general_holdings(heldBy="NY", limit=20)
                assert msg in str(exc.value)

    def test_search_general_holdings_invalid_oclc_number(self, mock_token):
        msg = "Invalid OCLC # was passed as an argument"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_general_holdings(oclcNumber="odn12345")
                assert msg in str(exc.value)

    def test_search_general_holdings_with_stale_token(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            mock_token.token_expires_at = datetime.strftime(
                datetime.utcnow() - timedelta(0, 1), "%Y-%m-%d %H:%M:%SZ"
            )
            assert mock_token.is_expired() is True
            response = session.search_general_holdings(oclcNumber=12345)
            assert mock_token.is_expired() is False
            assert response.status_code == 200

    def test_search_general_holdings_timout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_general_holdings(oclcNumber="12345")

    def test_search_general_holdings_connectionerror(
        self, mock_token, mock_connectionerror
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_general_holdings(oclcNumber=12345)

    def test_search_general_holdings_unexpectederror(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_general_holdings(oclcNumber="12345")

    def test_search_general_holdings_400_error_response(
        self, mock_token, mock_400_response
    ):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_general_holdings(oclcNumber=12345)
                assert msg in str(exc.value)


@pytest.mark.webtest
class TestLiveMetadataSession:
    """Runs rudimentary tests against live Metadata API"""

    def test_brief_bib_print_mat_request(self, live_keys):
        fields = sorted(
            [
                "catalogingInfo",
                "creator",
                "date",
                "edition",
                "generalFormat",
                "language",
                "mergedOclcNumbers",
                "oclcNumber",
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

    def test_brief_bib_401_error(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )
        token.token_str = "invalid-token"
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": f"Bearer invalid-token"})
            with pytest.raises(WorldcatSessionError) as exc:
                session.get_brief_bib(41266045)
                response_msg = "Web service returned 401 error: {'message': 'Unauthorized'}; https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
                assert response_msg in str(exc.value)

    def test_brief_bib_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bib_other_editions(41266045)

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
                itemSubType="printbook",
                catalogSource="dlc",
                orderedBy="mostWidelyHeld",
                limit=5,
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
            assert (
                response.request.url
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs?q=ti%3Azendegi+AND+au%3Aegan&inLanguage=eng&inCatalogLanguage=eng&itemType=book&itemSubType=printbook&catalogSource=dlc&orderedBy=mostWidelyHeld&limit=5"
            )

    def test_search_general_holdings(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_general_holdings(isbn="9781597801744")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
