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

    def test_new_url_base(self, stub_session):
        assert stub_session.URL_BASE() == "https://metadata.api.oclc.org/worldcat"

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

    def test_url_manage_bib(self, stub_session):
        assert (
            stub_session._url_manage_bib(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/12345"
        )

    def test_url_manage_bib_current_oclc_number(self, stub_session):
        assert (
            stub_session._url_manage_bib_current_oclc_number()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/current"
        )

    def test_url_bib_holding_libraries(self, stub_session):
        assert (
            stub_session._url_bib_holding_libraries()
            == "https://worldcat.org/bib/holdinglibraries"
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
        with pytest.raises(InvalidOclcNumber):
            stub_session.get_brief_bib(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_get_brief_bib_with_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        assert stub_session.authorization.is_expired() is True
        response = stub_session.get_brief_bib(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
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
        assert stub_session.get_institution_holdings("12345").status_code == 200

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

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (None, pytest.raises(InvalidOclcNumber)),
            ([], pytest.raises(InvalidOclcNumber)),
            (["bt2111111111"], pytest.raises(InvalidOclcNumber)),
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

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            (None, pytest.raises(InvalidOclcNumber)),
            ([], pytest.raises(InvalidOclcNumber)),
            (["bt2111111111"], pytest.raises(InvalidOclcNumber)),
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
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_unset([850940548, 850940552, 850940554])
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
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
        with pytest.raises(InvalidOclcNumber):
            stub_session.holdings_set_multi_institutions(
                oclcNumber="odn1234", instSymbols="NYP,BKL"
            )

    @pytest.mark.http_code(200)
    def test_holdings_set_multi_institutions_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_set_multi_institutions(
                oclcNumber=850940548, instSymbols="NYP,BKL"
            )
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
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
            "403 Client Error: 'foo' for url: https://foo.bar?query. Server response: spam"
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
        with pytest.raises(InvalidOclcNumber):
            stub_session.holdings_unset_multi_institutions(
                oclcNumber="odn1234", instSymbols="NYP,BKL"
            )

    @pytest.mark.http_code(200)
    def test_holdings_unset_multi_institutions_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        with does_not_raise():
            assert stub_session.authorization.is_expired() is True
            stub_session.holdings_unset_multi_institutions(
                oclcNumber=850940548, instSymbols="NYP,BKL"
            )
            assert stub_session.authorization.token_expires_at == datetime.datetime(
                2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
            )
            assert stub_session.authorization.is_expired() is False

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions(
        self, stub_session, mock_session_response
    ):
        assert stub_session.search_brief_bib_other_editions(12345).status_code == 200

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_other_editions_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_brief_bib_other_editions(12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

    def test_search_brief_bibs_other_editions_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_brief_bib_other_editions("odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_seach_brief_bibs(self, stub_session, mock_session_response):
        assert stub_session.search_brief_bibs(q="ti:Zendegi").status_code == 200

    @pytest.mark.parametrize("argm", [(None), ("")])
    def test_search_brief_bibs_missing_query(self, stub_session, argm):
        with pytest.raises(TypeError) as exc:
            stub_session.search_brief_bibs(argm)
        assert "Argument 'q' is requried to construct query." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_brief_bibs_with_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_brief_bibs(q="ti:foo")
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
        )
        assert stub_session.authorization.is_expired() is False
        assert response.status_code == 200

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
    def test_search_general_holdings(self, stub_session, mock_session_response):
        assert stub_session.search_general_holdings(oclcNumber=12345).status_code == 200

    def test_search_general_holdings_missing_arguments(self, stub_session):
        msg = "Missing required argument. One of the following args are required: oclcNumber, issn, isbn"
        with pytest.raises(TypeError) as exc:
            stub_session.search_general_holdings(holdingsAllEditions=True, limit=20)
        assert msg in str(exc.value)

    def test_search_general_holdings_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_general_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_general_holdings_with_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_general_holdings(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
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
        with pytest.raises(TypeError) as exc:
            stub_session.search_shared_print_holdings(heldInState="NY", limit=20)
        assert msg in str(exc.value)

    def test_search_shared_print_holdings_with_invalid_oclc_number_passsed(
        self, stub_session
    ):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.search_shared_print_holdings(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_search_shared_print_holdings_with_stale_token(
        self, mock_now, stub_session, mock_session_response
    ):
        stub_session.authorization.token_expires_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(0, 1)
        assert stub_session.authorization.is_expired() is True
        response = stub_session.search_shared_print_holdings(oclcNumber=12345)
        assert stub_session.authorization.token_expires_at == datetime.datetime(
            2020, 1, 1, 17, 19, 58, tzinfo=datetime.timezone.utc
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

    def test_get_current_oclc_number(self, live_keys):
        token = WorldcatAccessToken(
            key=os.getenv("WCKey"),
            secret=os.getenv("WCSecret"),
            scopes=os.getenv("WCScopes"),
            principal_id=os.getenv("WCPrincipalID"),
            principal_idns=os.getenv("WCPrincipalIDNS"),
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
