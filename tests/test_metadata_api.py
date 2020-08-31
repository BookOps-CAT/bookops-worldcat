# -*- coding: utf-8 -*-

import os

import pytest
import requests

from bookops_worldcat import MetadataSession, WorldcatAccessToken


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
        with pytest.raises(TypeError) as exc:
            MetadataSession()
            assert (
                "Argument 'authorization' must include 'WorldcatAccessToken' obj."
                in str(exc.value)
            )

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
                session._url_brief_bib_oclc_number(oclc_number=argm)
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345"
            )

    def test_url_brief_bib_other_editions(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_other_editions(oclc_number="12345")
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345/other-editions"
            )

    def test_url_lhr_control_number(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_lhr_control_number(control_number="12345")
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
                session._url_bib_oclc_number(oclc_number="12345")
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

    def test_get_brief_bib_timout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(requests.exceptions.Timeout):
                session.get_brief_bib(12345)

    def test_get_brief_bib_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(requests.exceptions.ConnectionError):
                session.get_brief_bib(12345)

    def test_get_brief_bib_other_editions(
        self, mock_token, mock_successful_session_get_request
    ):
        with MetadataSession(authorization=mock_token) as session:
            assert session.get_brief_bib_other_editions(12345).status_code == 200

    def test_get_brief_bib_other_editions_timout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(requests.exceptions.Timeout):
                session.get_brief_bib_other_editions(12345)

    def test_get_brief_bib_other_editions_connectionerror(
        self, mock_token, mock_connectionerror
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(requests.exceptions.ConnectionError):
                session.get_brief_bib_other_editions(12345)


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

    def test_brief_bib_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.get_brief_bib_other_editions(41266045)

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
