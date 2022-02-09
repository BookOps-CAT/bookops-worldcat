# -*- coding: utf-8 -*-

from contextlib import contextmanager
import datetime
import os

import pytest


from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import WorldcatSessionError


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
        err_msg = "Argument 'authorization' must include 'WorldcatAccessToken' object."
        with pytest.raises(WorldcatSessionError) as exc:
            MetadataSession(authorization="my_token")
        assert err_msg in str(exc.value)

    def test_get_new_access_token(self, mock_token, mock_utcnow):
        assert mock_token.is_expired() is False
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            session._get_new_access_token()
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False

    def test_get_new_access_token_exceptions(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session._get_new_access_token()

    @pytest.mark.parametrize(
        "oclcNumbers,buckets,expectation",
        [
            ([], 0, []),
            (["1", "2", "3"], 1, ["1,2,3"]),
            ([1, 2, 3], 1, ["1,2,3"]),
            (["1"], 1, ["1"]),
            (["1"] * 50, 1, [",".join(["1"] * 50)]),
            (["1"] * 51, 2, [",".join(["1"] * 50), "1"]),
            (
                ["1"] * 103,
                3,
                [",".join(["1"] * 50), ",".join(["1"] * 50), "1,1,1"],
            ),
        ],
    )
    def test_split_into_legal_volume(
        self, mock_token, oclcNumbers, buckets, expectation
    ):
        token = mock_token
        with MetadataSession(authorization=token) as session:
            assert session._split_into_legal_volume(oclcNumbers) == expectation

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

    def test_get_brief_bib(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.get_brief_bib(12345).status_code == 200

    def test_get_brief_bib_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.get_brief_bib()

    def test_get_brief_bib_None_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_brief_bib(oclcNumber=None)

    def test_get_brief_bib_with_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.get_brief_bib(oclcNumber=12345)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

    def test_get_brief_bib_timeout(self, mock_token, mock_timeout):
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

    def test_get_full_bib(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.get_full_bib(12345).status_code == 200

    def test_get_full_bib_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.get_full_bib()

    def test_get_full_bib_None_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_full_bib(oclcNumber=None)

    def test_get_full_bib_with_stale_token(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.get_full_bib(12345)
            assert session.authorization.is_expired() is False
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert response.status_code == 200

    def test_get_full_bib_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_full_bib(12345)

    def test_get_full_bib_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_full_bib(12345)

    def test_get_full_bib_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.get_full_bib(12345)

    def test_get_full_bib_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.get_full_bib(12345)
            assert msg in str(exc.value)

    def test_holding_get_status(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.holding_get_status(12345).status_code == 200

    def test_holding_get_status_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.holding_get_status()

    def test_holding_get_status_None_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_get_status(oclcNumber=None)

    def test_holding_get_status_with_stale_token(
        self, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.holding_get_status(12345)
            assert session.authorization.is_expired() is False
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert response.status_code == 200

    def test_holding_get_status_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_get_status(12345)

    def test_holding_get_status_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_get_status(12345)

    def test_holding_get_status_unexpected_error(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_get_status(12345)

    def test_holding_status_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.holding_get_status(12345)
            assert msg in str(exc.value)

    @pytest.mark.http_code(201)
    def test_holding_set(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.holding_set(850940548).status_code == 201

    def test_holding_set_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.holding_set()

    def test_holding_set_None_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_set(oclcNumber=None)

    @pytest.mark.http_code(201)
    def test_holding_set_stale_token(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.holding_set(850940548)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 201

    def test_holding_set_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_set(850940548)

    def test_holding_set_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_set(850940548)

    def test_holding_set_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_set(850940548)

    def test_holding_set_409_error_response(self, mock_token, mock_409_response):
        msg = {
            "code": {"value": "WS-409", "type": "application"},
            "message": "Trying to set hold while holding already exists",
            "detail": None,
        }
        with MetadataSession(authorization=mock_token) as session:
            response = session.holding_set(850940548)
            assert response.json() == msg

    def test_holding_set_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.holding_set(850940548)
            assert msg in str(exc.value)

    def test_holding_unset(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.holding_unset(850940548).status_code == 200

    def test_holding_unset_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.holding_unset()

    def test_holding_unset_None_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_unset(oclcNumber=None)

    def test_holding_unset_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.holding_unset(850940548)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

    def test_holding_unset_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_unset(850940548)

    def test_holding_unset_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_unset(850940548)

    def test_holding_unset_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_unset(850940548)

    def test_holding_unset_409_error_response(self, mock_token, mock_409_response):
        # cheating here a bit, response is bit different
        msg = {
            "code": {"value": "WS-409", "type": "application"},
            "message": "Trying to set hold while holding already exists",
            "detail": None,
        }
        with MetadataSession(authorization=mock_token) as session:
            response = session.holding_unset(850940548)
            assert response.json() == msg

    def test_holding_unset_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.holding_unset(850940548)
            assert msg in str(exc.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (None, pytest.raises(WorldcatSessionError)),
            ([], pytest.raises(WorldcatSessionError)),
            (["bt2111111111"], pytest.raises(WorldcatSessionError)),
            (["850940548"], does_not_raise()),
            (["ocn850940548"], does_not_raise()),
            ("850940548,850940552, 850940554", does_not_raise()),
            (["850940548", "850940552", "850940554"], does_not_raise()),
            ([850940548, 850940552, 850940554], does_not_raise()),
        ],
    )
    @pytest.mark.http_code(207)
    def test_holdings_set(self, argm, expectation, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            with expectation:
                session.holdings_set(argm)

    def test_holdings_set_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.holdings_set()

    @pytest.mark.http_code(207)
    def test_holdings_set_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            with does_not_raise():
                assert session.authorization.is_expired() is True
                session.holdings_set([850940548, 850940552, 850940554])
                assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
                assert session.authorization.is_expired() is False

    def test_holdings_set_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holdings_set([850940548, 850940552, 850940554])

    def test_holdings_set_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_set([850940548, 850940552, 850940554])

    def test_holdings_set_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holdings_set([850940548, 850940552, 850940554])

    def test_holdings_set_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.holdings_set([850940548, 850940552, 850940554])
            assert msg in str(exc.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (None, pytest.raises(WorldcatSessionError)),
            ([], pytest.raises(WorldcatSessionError)),
            (["bt2111111111"], pytest.raises(WorldcatSessionError)),
            (["850940548"], does_not_raise()),
            (["ocn850940548"], does_not_raise()),
            ("850940548,850940552, 850940554", does_not_raise()),
            (["850940548", "850940552", "850940554"], does_not_raise()),
            ([850940548, 850940552, 850940554], does_not_raise()),
        ],
    )
    @pytest.mark.http_code(207)
    def test_holdings_unset(self, argm, expectation, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            with expectation:
                session.holdings_unset(argm)

    def test_holdings_unset_no_oclcNumber_passed(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(TypeError):
                session.holdings_unset()

    @pytest.mark.http_code(207)
    def test_holdings_unset_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            with does_not_raise():
                assert session.authorization.is_expired() is True
                session.holdings_unset([850940548, 850940552, 850940554])
                assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
                assert session.authorization.is_expired() is False

    def test_holdings_uset_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holdings_unset([850940548, 850940552, 850940554])

    def test_holdings_unset_connectionerror(self, mock_token, mock_connectionerror):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holding_unset([850940548, 850940552, 850940554])

    def test_holdings_unset_unexpected_error(self, mock_token, mock_unexpected_error):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.holdings_unset([850940548, 850940552, 850940554])

    def test_holdings_unset_400_error_response(self, mock_token, mock_400_response):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.holdings_unset([850940548, 850940552, 850940554])
            assert msg in str(exc.value)

    def test_search_brief_bibs_other_editions(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_brief_bib_other_editions(12345).status_code == 200

    def test_search_brief_bibs_other_editions_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.search_brief_bib_other_editions(12345)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

    def test_search_brief_bib_other_editions_timeout(self, mock_token, mock_timeout):
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

    def test_seach_brief_bibs(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, mock_token, argm):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_brief_bibs(argm)
            assert "Argument 'q' is requried to construct query." in str(exc.value)

    def test_search_brief_bibs_with_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.search_brief_bibs(q="ti:foo")
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
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

    @pytest.mark.http_code(207)
    def test_seach_current_control_numbers(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session.search_current_control_numbers(
                    oclcNumbers=["12345", "65891"]
                ).status_code
                == 207
            )

    @pytest.mark.http_code(207)
    def test_seach_current_control_numbers_passed_as_str(
        self, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session.search_current_control_numbers(
                    oclcNumbers="12345,65891"
                ).status_code
                == 207
            )

    @pytest.mark.parametrize("argm", [(None), (""), ([])])
    def test_search_current_control_numbers_missing_numbers(self, mock_token, argm):
        err_msg = "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #."
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_current_control_numbers(argm)
            assert err_msg in str(exc.value)

    @pytest.mark.http_code(207)
    def test_search_current_control_numbers_with_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.search_current_control_numbers(["12345", "65891"])
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 207

    def test_search_current_control_numbers_timeout(self, mock_token, mock_timeout):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_current_control_numbers(["12345", "65891"])

    def test_search_current_control_numbers_connectionerror(
        self, mock_token, mock_connectionerror
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_current_control_numbers(["12345", "65891"])

    def test_search_current_control_numbers_unexpected_error(
        self, mock_token, mock_unexpected_error
    ):
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError):
                session.search_current_control_numbers(["12345", "65891"])

    def test_search_current_control_numbers_400_error_response(
        self, mock_token, mock_400_response
    ):
        msg = "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_current_control_numbers(["12345", "65891"])
            assert msg in str(exc.value)

    def test_search_general_holdings(self, mock_token, mock_session_response):
        with MetadataSession(authorization=mock_token) as session:
            assert session.search_general_holdings(oclcNumber=12345).status_code == 200

    def test_search_general_holdings_missing_arguments(self, mock_token):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_general_holdings(holdingsAllEditions=True, limit=20)
            assert msg in str(exc.value)

    def test_search_general_holdings_invalid_oclc_number(self, mock_token):
        msg = "Invalid OCLC # was passed as an argument"
        with MetadataSession(authorization=mock_token) as session:
            with pytest.raises(WorldcatSessionError) as exc:
                session.search_general_holdings(oclcNumber="odn12345")
            assert msg in str(exc.value)

    def test_search_general_holdings_with_stale_token(
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.search_general_holdings(oclcNumber=12345)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

    def test_search_general_holdings_timeout(self, mock_token, mock_timeout):
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

    def test_search_shared_print_holdings(self, mock_token, mock_session_response):
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
        self, mock_utcnow, mock_token, mock_session_response
    ):
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.search_shared_print_holdings(oclcNumber=12345)
            assert session.authorization.token_expires_at == "2020-01-01 17:19:58Z"
            assert session.authorization.is_expired() is False
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
        err_msg = 'Web service returned 401 error: {"message":"Unauthorized"}; https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045'
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": f"Bearer invalid-token"})
            with pytest.raises(WorldcatSessionError) as exc:
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
            session.authorization.token_expires_at = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(0, 1),
                "%Y-%m-%d %H:%M:%SZ",
            )
            assert session.authorization.is_expired() is True
            response = session.get_brief_bib(oclcNumber=41266045)
            assert session.authorization.is_expired() is False
            assert response.status_code == 200

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

            assert response.url == "https://worldcat.org/bib/data/41266045"
            assert response.status_code == 200

    def test_holding_get_status(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holding_get_status(982651100)

            assert (
                response.url
                == "https://worldcat.org/ih/checkholdings?oclcNumber=982651100"
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == ["content", "title", "updated"]
            assert sorted(response.json()["content"].keys()) == sorted(
                [
                    "requestedOclcNumber",
                    "currentOclcNumber",
                    "institution",
                    "holdingCurrentlySet",
                    "id",
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
            response = session.holding_get_status(850940548)
            holdings = response.json()["content"]["holdingCurrentlySet"]

            # make sure no holdings are set initially
            if holdings is True:
                response = session.holding_unset(850940548)

            response = session.holding_set(
                850940548, response_format="application/atom+json"
            )
            assert response.url == "https://worldcat.org/ih/data?oclcNumber=850940548"
            assert response.status_code == 201
            assert response.text == ""

            # test setting holdings on bib with already existing holding
            response = session.holding_set(850940548)
            assert response.status_code == 409
            assert response.url == "https://worldcat.org/ih/data?oclcNumber=850940548"
            assert response.json() == {
                "code": {"value": "WS-409", "type": "application"},
                "message": "Trying to set hold while holding already exists",
                "detail": None,
            }

            # test deleting holdings
            response = session.holding_unset(850940548)
            assert response.status_code == 200
            assert (
                response.request.url
                == "https://worldcat.org/ih/data?oclcNumber=850940548&cascade=0"
            )
            assert response.text == ""

            # test deleting holdings on bib without any
            response = session.holding_unset(850940548)
            assert response.status_code == 409
            assert (
                response.request.url
                == "https://worldcat.org/ih/data?oclcNumber=850940548&cascade=0"
            )
            assert response.json() == {
                "code": {"value": "WS-409", "type": "application"},
                "message": "Trying to unset hold while holding does not exist",
                "detail": None,
            }

    @pytest.mark.holdings
    def test_holdings_set(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_set([850940548, 850940552, 850940554])
            assert type(response) is list
            assert response[0].status_code == 207
            assert (
                response[0].url
                == "https://worldcat.org/ih/datalist?oclcNumbers=850940548%2C850940552%2C850940554"
            )
            assert sorted(response[0].json().keys()) == sorted(
                ["entries", "extensions"]
            )
            assert sorted(response[0].json()["entries"][0]) == sorted(
                ["title", "content", "updated"]
            )
            assert sorted(response[0].json()["entries"][0]["content"]) == sorted(
                [
                    "requestedOclcNumber",
                    "currentOclcNumber",
                    "institution",
                    "status",
                    "detail",
                ]
            )

    @pytest.mark.holdings
    def test_holdings_unset(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.holdings_unset([850940548, 850940552, 850940554])
            assert type(response) is list
            assert response[0].status_code == 207
            assert (
                response[0].url
                == "https://worldcat.org/ih/datalist?oclcNumbers=850940548%2C850940552%2C850940554&cascade=0"
            )
            assert sorted(response[0].json().keys()) == sorted(
                ["entries", "extensions"]
            )
            assert sorted(response[0].json()["entries"][0]) == sorted(
                ["title", "content", "updated"]
            )
            assert sorted(response[0].json()["entries"][0]["content"]) == sorted(
                [
                    "requestedOclcNumber",
                    "currentOclcNumber",
                    "institution",
                    "status",
                    "detail",
                ]
            )

    def test_brief_bib_other_editions(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
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
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_brief_bibs(
                "ti:zendegi AND au:egan",
                inLanguage="eng",
                inCatalogLanguage="eng",
                itemType="book",
                # itemSubType="printbook",
                catalogSource="dlc",
                orderBy="mostWidelyHeld",
                limit=5,
            )
            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields
            # removed temp &itemSubType=printbook due to OCLC error/issue
            assert (
                response.request.url
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs?q=ti%3Azendegi+AND+au%3Aegan&inLanguage=eng&inCatalogLanguage=eng&catalogSource=dlc&itemType=book&orderBy=mostWidelyHeld&limit=5"
            )

    def test_search_general_holdings(self, live_keys):
        fields = sorted(["briefRecords", "numberOfRecords"])
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_general_holdings(isbn="9781597801744")

            assert response.status_code == 200
            assert sorted(response.json().keys()) == fields

    def test_search_current_control_numbers(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
        )

        with MetadataSession(authorization=token) as session:
            response = session.search_current_control_numbers([41266045, 519740398])

            assert response.status_code == 207
            assert (
                response.request.url
                == "https://worldcat.org/bib/checkcontrolnumbers?oclcNumbers=41266045%2C519740398"
            )
            jres = response.json()
            assert sorted(jres.keys()) == ["entries", "extensions"]
            assert sorted(jres["entries"][0].keys()) == ["content", "title", "updated"]
            assert sorted(jres["entries"][0]["content"].keys()) == sorted(
                [
                    "currentOclcNumber",
                    "detail",
                    "found",
                    "id",
                    "institution",
                    "merged",
                    "requestedOclcNumber",
                    "status",
                ]
            )
