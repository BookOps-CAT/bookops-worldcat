# -*- coding: utf-8 -*-

from contextlib import contextmanager
import datetime
import os
from types import GeneratorType

import pytest


from bookops_worldcat import MetadataSession, WorldcatAccessToken
from bookops_worldcat.errors import WorldcatSessionError, WorldcatRequestError


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
        with pytest.raises(WorldcatSessionError) as exc:
            MetadataSession(authorization="my_token")
        assert err_msg in str(exc.value)

    def test_get_new_access_token(self, mock_token, mock_utcnow):
        assert mock_token.is_expired() is False
        with MetadataSession(authorization=mock_token) as session:
            session.authorization.token_expires_at = (
                datetime.datetime.utcnow() - datetime.timedelta(0, 1)
            )
            assert session.authorization.is_expired() is True
            session._get_new_access_token()
            assert session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58
            )
            assert session.authorization.is_expired() is False

    def test_get_new_access_token_exceptions(self, stub_session, mock_timeout):
        with pytest.raises(WorldcatSessionError):
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
        assert stub_session._url_base() == "https://worldcat.org"

    def test_url_search_base(self, stub_session):
        assert (
            stub_session._url_search_base()
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1"
        )

    def test_url_shared_print_holdings(self, stub_session):
        assert (
            stub_session._url_member_shared_print_holdings()
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/bibs-retained-holdings"
        )

    def test_url_member_general_holdings(self, stub_session):
        assert (
            stub_session._url_member_general_holdings()
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/bibs-summary-holdings"
        )

    def test_url_brief_bib_search(self, stub_session):
        assert (
            stub_session._url_brief_bib_search()
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
    def test_url_brief_bib_oclc_number(self, argm, expectation, stub_session):
        assert (
            stub_session._url_brief_bib_oclc_number(oclcNumber=argm)
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345"
        )

    def test_url_brief_bib_other_editions(self, stub_session):
        assert (
            stub_session._url_brief_bib_other_editions(oclcNumber="12345")
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345/other-editions"
        )

    def test_url_lhr_control_number(self, stub_session):
        assert (
            stub_session._url_lhr_control_number(controlNumber="12345")
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/my-holdings/12345"
        )

    def test_url_lhr_search(self, stub_session):
        assert (
            stub_session._url_lhr_search()
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/my-holdings"
        )

    def test_url_lhr_shared_print(self, stub_session):
        assert (
            stub_session._url_lhr_shared_print()
            == "https://americas.metadata.api.oclc.org/worldcat/search/v1/retained-holdings"
        )

    def test_url_bib_oclc_number(self, stub_session):
        assert (
            stub_session._url_bib_oclc_number(oclcNumber="12345")
            == "https://worldcat.org/bib/data/12345"
        )

    def test_url_bib_check_oclc_numbers(self, stub_session):
        assert (
            stub_session._url_bib_check_oclc_numbers()
            == "https://worldcat.org/bib/checkcontrolnumbers"
        )

    def test_url_bib_holding_libraries(self, stub_session):
        assert (
            stub_session._url_bib_holding_libraries()
            == "https://worldcat.org/bib/holdinglibraries"
        )

    def test_url_bib_holdings_action(self, stub_session):
        assert stub_session._url_bib_holdings_action() == "https://worldcat.org/ih/data"

    def test_url_bib_holdings_check(self, stub_session):
        assert (
            stub_session._url_bib_holdings_check()
            == "https://worldcat.org/ih/checkholdings"
        )

    def test_url_bib_holdings_batch_action(self, stub_session):
        assert (
            stub_session._url_bib_holdings_batch_action()
            == "https://worldcat.org/ih/datalist"
        )

    def test_url_bib_holdings_multi_institution_batch_action(self, stub_session):
        assert (
            stub_session._url_bib_holdings_multi_institution_batch_action()
            == "https://worldcat.org/ih/institutionlist"
        )

    @pytest.mark.http_code(200)
    def test_get_brief_bib(self, stub_session, mock_session_response):
        assert stub_session.get_brief_bib(12345).status_code == 200

    def test_get_brief_bib_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_brief_bib()

    def test_get_brief_bib_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.get_brief_bib(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_get_brief_bib_with_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.get_brief_bib(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

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
            "404 Client Error: 'foo' for url: https://foo.bar?query. Server response: b'spam'"
            in (str(exc.value))
        )

    @pytest.mark.http_code(200)
    def test_get_full_bib(self, stub_session, mock_session_response):
        assert stub_session.get_full_bib(12345).status_code == 200

    def test_get_full_bib_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.get_full_bib()

    def test_get_full_bib_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.get_full_bib(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_get_full_bib_with_stale_token(self, stub_session, mock_session_response):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )

        assert stub_session.authorization.is_expired() is True
        response = stub_session.get_full_bib(12345)
        assert stub_session.authorization.is_expired() is False
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert response.status_code == 200

    @pytest.mark.http_code(200)
    def test_holding_get_status(self, stub_session, mock_session_response):
        assert stub_session.holding_get_status(12345).status_code == 200

    def test_holding_get_status_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holding_get_status()

    def test_holding_get_status_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.holding_get_status(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_holding_get_status_with_stale_token(
        self, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.holding_get_status(12345)
        assert stub_session.authorization.is_expired() is False
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert response.status_code == 200

    @pytest.mark.http_code(201)
    def test_holding_set(self, stub_session, mock_session_response):
        assert stub_session.holding_set(850940548).status_code == 201

    def test_holding_set_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holding_set()

    def test_holding_set_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.holding_set(oclcNumber=None)

    @pytest.mark.http_code(201)
    def test_holding_set_stale_token(self, stub_session, mock_session_response):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.holding_set(850940548)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 201

    @pytest.mark.http_code(200)
    def test_holding_unset(self, stub_session, mock_session_response):
        assert stub_session.holding_unset(850940548).status_code == 200

    def test_holding_unset_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holding_unset()

    def test_holding_unset_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.holding_unset(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_holding_unset_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.holding_unset(850940548)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

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
    def test_holdings_set(self, argm, expectation, stub_session, mock_session_response):
        with expectation:
            stub_session.holdings_set(argm)

    def test_holdings_set_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_set()

    @pytest.mark.http_code(207)
    def test_holdings_set_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_set([850940548, 850940552, 850940554])
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58
            )
            assert stub_session.authorization.is_expired() is False

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
    def test_holdings_unset(
        self, argm, expectation, stub_session, mock_session_response
    ):
        with expectation:
            stub_session.holdings_unset(argm)

    def test_holdings_unset_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_unset()

    @pytest.mark.http_code(207)
    def test_holdings_unset_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_unset([850940548, 850940552, 850940554])
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58
            )
            assert stub_session.authorization.is_expired() is False

    @pytest.mark.http_code(200)
    def test_holdings_set_multi_institutions(self, stub_session, mock_session_response):
        results = stub_session.holdings_set_multi_institutions(
            oclcNumber=850940548, instSymbols="BKL,NYP"
        )
        assert results.status_code == 200

    def test_holdings_set_multi_institutions_missing_oclc_number(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_set_multi_institutions(instSymbols="NYP,BKL")

    def test_holdings_set_multi_institutions_missing_inst_symbols(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_set_multi_institutions(oclcNumber=123)

    def test_holdings_set_multi_institutions_invalid_oclc_number(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.holdings_set_multi_institutions(
                oclcNumber="odn1234", instSymbols="NYP,BKL"
            )

    @pytest.mark.http_code(200)
    def test_holdings_set_multi_institutions_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_set_multi_institutions(
                oclcNumber=850940548, instSymbols="NYP,BKL"
            )
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58
            )
            assert stub_session.authorization.is_expired() is False

    @pytest.mark.http_code(403)
    def test_holdings_set_multi_institutions_permission_error(
        self, stub_session, mock_session_response
    ):
        with pytest.raises(WorldcatRequestError) as exc:
            stub_session.holdings_set_multi_institutions(
                oclcNumber=850940548, instSymbols="NYP,BKL"
            )

        assert (
            "403 Client Error: 'foo' for url: https://foo.bar?query. Server response: b'spam'"
            in str(exc.value)
        )

    @pytest.mark.http_code(200)
    def test_holdings_unset_multi_institutions(
        self, stub_session, mock_session_response
    ):
        results = stub_session.holdings_unset_multi_institutions(
            850940548, "BKL,NYP", cascade="1"
        )
        assert results.status_code == 200

    def test_holdings_unset_multi_institutions_missing_oclc_number(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_unset_multi_institutions(instSymbols="NYP,BKL")

    def test_holdings_unset_multi_institutions_missing_inst_symbols(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_unset_multi_institutions(oclcNumber=123)

    def test_holdings_unset_multi_institutions_invalid_oclc_number(self, stub_session):
        with pytest.raises(WorldcatSessionError):
            stub_session.holdings_unset_multi_institutions(
                oclcNumber="odn1234", instSymbols="NYP,BKL"
            )

    @pytest.mark.http_code(200)
    def test_holdings_unset_multi_institutions_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_unset_multi_institutions(
                oclcNumber=850940548, instSymbols="NYP,BKL"
            )
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58
            )
            assert stub_session.authorization.is_expired() is False

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions(
        self, stub_session, mock_session_response
    ):
        assert stub_session.search_brief_bib_other_editions(12345).status_code == 200

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_brief_bib_other_editions(12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

    def test_search_brief_bibs_other_editions_invalid_oclc_number(self, stub_session):
        msg = "Invalid OCLC # was passed as an argument"
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_brief_bib_other_editions("odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_seach_brief_bibs(self, stub_session, mock_session_response):
        assert stub_session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, stub_session, argm):
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_brief_bibs(argm)
        assert "Argument 'q' is requried to construct query." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_with_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_brief_bibs(q="ti:foo")
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

    @pytest.mark.http_code(207)
    def test_seach_current_control_numbers(self, stub_session, mock_session_response):
        assert (
            stub_session.search_current_control_numbers(
                oclcNumbers=["12345", "65891"]
            ).status_code
            == 207
        )

    @pytest.mark.http_code(207)
    def test_seach_current_control_numbers_passed_as_str(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.search_current_control_numbers(
                oclcNumbers="12345,65891"
            ).status_code
            == 207
        )

    @pytest.mark.parametrize("argm", [(None), (""), ([])])
    def test_search_current_control_numbers_missing_numbers(self, stub_session, argm):
        err_msg = "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #."
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_current_control_numbers(argm)
        assert err_msg in str(exc.value)

    @pytest.mark.http_code(207)
    def test_search_current_control_numbers_with_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_current_control_numbers(["12345", "65891"])
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 207

    @pytest.mark.http_code(200)
    def test_search_general_holdings(self, stub_session, mock_session_response):
        assert stub_session.search_general_holdings(oclcNumber=12345).status_code == 200

    def test_search_general_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_general_holdings(holdingsAllEditions=True, limit=20)
        assert msg in str(exc.value)

    def test_search_general_holdings_invalid_oclc_number(self, stub_session):
        msg = "Invalid OCLC # was passed as an argument"
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_general_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_general_holdings_with_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_general_holdings(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

    @pytest.mark.http_code(200)
    def test_search_shared_print_holdings(self, stub_session, mock_session_response):
        assert (
            stub_session.search_shared_print_holdings(oclcNumber=12345).status_code
            == 200
        )

    def test_search_shared_print_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_shared_print_holdings(heldInState="NY", limit=20)
        assert msg in str(exc.value)

    def test_search_shared_print_holdings_with_invalid_oclc_number_passsed(
        self, stub_session
    ):
        msg = "Invalid OCLC # was passed as an argument"
        with pytest.raises(WorldcatSessionError) as exc:
            stub_session.search_shared_print_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_shared_print_holdings_with_stale_token(
        self, mock_utcnow, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = (
            datetime.datetime.utcnow() - datetime.timedelta(0, 1)
        )
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_shared_print_holdings(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200


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
        err_msg = "401 Client Error: Unauthorized for url: https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/41266045"
        with MetadataSession(authorization=token) as session:
            session.headers.update({"Authorization": f"Bearer invalid-token"})
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
            session.authorization.token_expires_at = (
                datetime.datetime.utcnow() - datetime.timedelta(0, 1)
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
