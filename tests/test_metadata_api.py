# -*- coding: utf-8 -*-

import datetime
from contextlib import nullcontext as does_not_raise

import pytest

from bookops_worldcat import MetadataSession
from bookops_worldcat.errors import (
    InvalidOclcNumber,
    WorldcatAuthorizationError,
    WorldcatRequestError,
)


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

    def test_invalid_authorization(self):
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

    def test_url_base(self, stub_session):
        assert stub_session.BASE_URL == "https://metadata.api.oclc.org/worldcat"

    @pytest.mark.parametrize(
        "validationLevel",
        ["vaildateFull", "validateAdd", "validateReplace"],
    )
    def test_url_manage_bibs_validate(self, validationLevel, stub_session):
        assert (
            stub_session._url_manage_bibs_validate(validationLevel)
            == f"https://metadata.api.oclc.org/worldcat/manage/bibs/validate/{validationLevel}"
        )

    def test_url_manage_bib_current_oclc_number(self, stub_session):
        assert (
            stub_session._url_manage_bibs_current_oclc_number()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/current"
        )

    def test_url_manage_bibs_create(self, stub_session):
        assert (
            stub_session._url_manage_bibs_create()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs"
        )

    def test_url_manage_bibs(self, stub_session):
        assert (
            stub_session._url_manage_bibs(oclcNumber="12345")
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/12345"
        )

    def test_url_manage_bibs_match(self, stub_session):
        assert (
            stub_session._url_manage_bibs_match()
            == "https://metadata.api.oclc.org/worldcat/manage/bibs/match"
        )

    def test_url_manage_ih_current(self, stub_session):
        assert (
            stub_session._url_manage_ih_current()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/current"
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

    def test_url_manage_ih_set_with_bib(self, stub_session):
        assert (
            stub_session._url_manage_ih_set_with_bib()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/set"
        )

    def test_url_manage_ih_unset_with_bib(self, stub_session):
        assert (
            stub_session._url_manage_ih_unset_with_bib()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/unset"
        )

    def test_url_manage_ih_codes(self, stub_session):
        assert (
            stub_session._url_manage_ih_codes()
            == "https://metadata.api.oclc.org/worldcat/manage/institution/holding-codes"
        )

    def test_url_manage_institution_config(self, stub_session):
        assert (
            stub_session._url_manage_institution_config()
            == "https://metadata.api.oclc.org/worldcat/manage/institution-config/branch-shelving-locations"
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

    def test_url_search_institution(self, stub_session):
        assert (
            stub_session._url_search_institution()
            == "https://metadata.api.oclc.org/worldcat/search/institution"
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

    @pytest.mark.parametrize(
        "argm",
        ["12345", 12345],
    )
    def test_url_search_bibs(self, argm, stub_session):
        assert (
            stub_session._url_search_bibs(oclcNumber=argm)
            == "https://metadata.api.oclc.org/worldcat/search/bibs/12345"
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
    def test_bib_create(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.bib_create(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_bib_get(self, stub_session, mock_session_response):
        assert stub_session.bib_get(12345).status_code == 200

    def test_bib_get_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.bib_get()

    def test_bib_get_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.bib_get(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_bib_get_classification(self, stub_session, mock_session_response):
        assert stub_session.bib_get_classification(12345).status_code == 200

    def test_bib_get_classification_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.bib_get_classification()

    @pytest.mark.parametrize(
        "argm", ["12345, 65891", ["12345", "65891"], 12345, ["12345", 12345]]
    )
    @pytest.mark.http_code(200)
    def test_bib_get_current_oclc_number(
        self, argm, stub_session, mock_session_response
    ):
        assert (
            stub_session.bib_get_current_oclc_number(oclcNumbers=argm).status_code
            == 200
        )

    @pytest.mark.parametrize("argm", [(None), (""), ([])])
    def test_bib_get_current_oclc_number_missing_numbers(self, stub_session, argm):
        err_msg = "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.bib_get_current_oclc_number(argm)
        assert err_msg in str(exc.value)

    def test_bib_get_current_oclc_number_too_many_oclcNumbers_passed(
        self, stub_session
    ):
        with pytest.raises(ValueError) as exc:
            stub_session.bib_get_current_oclc_number(
                oclcNumbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            )
        assert "Too many OCLC Numbers passed to 'oclcNumbers' argument." in str(
            exc.value
        )

    @pytest.mark.http_code(200)
    def test_bib_match(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.bib_match(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_bib_replace(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.bib_replace(
                "12345", stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_bib_search(self, stub_session, mock_session_response):
        assert stub_session.bib_search(12345).status_code == 200

    def test_bib_search_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.bib_search()

    def test_bib_search_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.bib_search(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_bib_validate(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.bib_validate(
                stub_marc_xml,
                recordFormat="application/marcxml+xml",
                validationLevel="validateFull",
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_bib_validate_default(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        assert (
            stub_session.bib_validate(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_bib_validate_error(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        with pytest.raises(ValueError) as exc:
            stub_session.bib_validate(
                stub_marc_xml,
                recordFormat="application/marcxml+xml",
                validationLevel="validateFoo",
            )
        assert "Invalid argument 'validationLevel'." in str(exc.value)

    @pytest.mark.http_code(200)
    def test_branch_holding_codes_get(self, stub_session, mock_session_response):
        assert stub_session.branch_holding_codes_get().status_code == 200

    @pytest.mark.http_code(200)
    def test_brief_bibs_get(self, stub_session, mock_session_response):
        assert stub_session.brief_bibs_get(12345).status_code == 200

    def test_brief_bibs_get_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.brief_bibs_get()

    def test_brief_bibs_get_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.brief_bibs_get(oclcNumber=None)

    @pytest.mark.http_code(206)
    def test_brief_bibs_get_odd_206_http_code(
        self, stub_session, mock_session_response
    ):
        with does_not_raise():
            response = stub_session.brief_bibs_get(12345)
        assert response.status_code == 206

    @pytest.mark.http_code(404)
    def test_brief_bibs_get_404_error_response(
        self, stub_session, mock_session_response
    ):
        with pytest.raises(WorldcatRequestError) as exc:
            stub_session.brief_bibs_get(12345)

        assert (
            "404 Client Error: 'foo' for url: https://foo.bar?query. Server response: spam"
            in (str(exc.value))
        )

    @pytest.mark.http_code(200)
    def test_brief_bibs_search(self, stub_session, mock_session_response):
        assert stub_session.brief_bibs_search(q="ti:Zendegi").status_code == 200

    @pytest.mark.http_code(200)
    def test_brief_bibs_get_other_editions(self, stub_session, mock_session_response):
        assert stub_session.brief_bibs_get_other_editions(12345).status_code == 200

    def test_brief_bibs_get_other_editions_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.brief_bibs_get_other_editions("odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_holdings_get_codes(self, stub_session, mock_session_response):
        assert stub_session.holdings_get_codes().status_code == 200

    @pytest.mark.parametrize(
        "argm",
        ["12345", 12345, ["12345", 12345], "12345, 67890"],
    )
    @pytest.mark.http_code(200)
    def test_holdings_get_current(self, argm, stub_session, mock_session_response):
        assert stub_session.holdings_get_current(argm).status_code == 200

    def test_holdings_get_current_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_get_current()

    def test_holdings_get_current_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.holdings_get_current(oclcNumbers=None)

    def test_holdings_get_current_too_many_oclcNumbers_passed(self, stub_session):
        with pytest.raises(ValueError) as exc:
            stub_session.holdings_get_current(
                oclcNumbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            )
        assert "Too many OCLC Numbers passed to 'oclcNumbers' argument." in str(
            exc.value
        )

    @pytest.mark.http_code(201)
    def test_holdings_set(self, stub_session, mock_session_response):
        assert stub_session.holdings_set(850940548).status_code == 201

    def test_holdings_set_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_set()

    def test_holdings_set_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.holdings_set(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_holdings_unset(self, stub_session, mock_session_response):
        assert stub_session.holdings_unset(850940548).status_code == 200

    @pytest.mark.http_code(200)
    def test_holdings_unset_cascadeDelete_false(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.holdings_unset(850940548, cascadeDelete=False).status_code
            == 200
        )

    def test_holdings_unset_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.holdings_unset()

    def test_holdings_unset_None_oclcNumber_passed(self, stub_session):
        with pytest.raises(InvalidOclcNumber):
            stub_session.holdings_unset(oclcNumber=None)

    @pytest.mark.http_code(200)
    def test_holdings_set_with_bib(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        assert (
            stub_session.holdings_set_with_bib(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_holdings_unset_with_bib(
        self, stub_session, mock_session_response, stub_marc_xml
    ):
        assert (
            stub_session.holdings_unset_with_bib(
                record=stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_institution_indentifiers_get_oclc_symbols(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.institution_indentifiers_get(oclcSymbols="FOO").status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_institution_indentifiers_get_registry_id(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.institution_indentifiers_get(registryIds="12345").status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_lbd_create(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.lbd_create(
                stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_lbd_delete(self, stub_session, mock_session_response):
        assert stub_session.lbd_delete("12345").status_code == 200

    @pytest.mark.http_code(200)
    def test_lbd_get(self, stub_session, mock_session_response):
        assert stub_session.lbd_get(12345).status_code == 200

    def test_lbd_get_no_controlNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.lbd_get()

    @pytest.mark.http_code(200)
    def test_lbd_replace(self, stub_session, mock_session_response, stub_marc_xml):
        assert (
            stub_session.lbd_replace(
                "12345", stub_marc_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_lhr_create(self, stub_session, mock_session_response, stub_holding_xml):
        assert (
            stub_session.lhr_create(
                stub_holding_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_lhr_delete(self, stub_session, mock_session_response):
        assert stub_session.lhr_delete("12345").status_code == 200

    @pytest.mark.http_code(200)
    def test_lhr_get(self, stub_session, mock_session_response):
        assert stub_session.lhr_get(12345).status_code == 200

    def test_lhr_get_no_controlNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.lhr_get()

    @pytest.mark.http_code(200)
    def test_lhr_replace(self, stub_session, mock_session_response, stub_holding_xml):
        assert (
            stub_session.lhr_replace(
                "12345", stub_holding_xml, recordFormat="application/marcxml+xml"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_local_bibs_get(self, stub_session, mock_session_response):
        assert stub_session.local_bibs_get(12345).status_code == 200

    def test_local_bibs_get_no_controlNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.local_bibs_get()

    @pytest.mark.http_code(200)
    def test_local_bibs_search(self, stub_session, mock_session_response):
        assert stub_session.local_bibs_search(q="ti:foo").status_code == 200

    @pytest.mark.http_code(200)
    def test_local_holdings_browse(self, stub_session, mock_session_response):
        assert (
            stub_session.local_holdings_browse(
                callNumber="12345", holdingLocation="foo", shelvingLocation="bar"
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_local_holdings_browse_oclc_number(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.local_holdings_browse(
                callNumber="12345",
                oclcNumber="54321",
                holdingLocation="foo",
                shelvingLocation="bar",
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_local_holdings_get(self, stub_session, mock_session_response):
        assert stub_session.local_holdings_get(12345).status_code == 200

    def test_local_holdings_get_no_controlNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.local_holdings_get()

    @pytest.mark.http_code(200)
    def test_local_holdings_search(self, stub_session, mock_session_response):
        assert stub_session.local_holdings_search(oclcNumber=12345).status_code == 200

    def test_local_holdings_search_no_oclcNumber_passed(
        self, stub_session, mock_session_response
    ):
        assert stub_session.local_holdings_search(barcode=12345).status_code == 200

    def test_local_holdings_search_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.local_holdings_search(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_local_holdings_search_shared_print(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.local_holdings_search_shared_print(
                oclcNumber=12345
            ).status_code
            == 200
        )

    @pytest.mark.http_code(200)
    def test_local_holdings_search_shared_print_no_oclcNumber_passed(
        self, stub_session, mock_session_response
    ):
        assert (
            stub_session.local_holdings_search_shared_print(barcode=12345).status_code
            == 200
        )

    def test_local_holdings_search_shared_print_with_invalid_oclc_number_passed(
        self, stub_session
    ):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.local_holdings_search_shared_print(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_summary_holdings_get(self, stub_session, mock_session_response):
        assert stub_session.summary_holdings_get(oclcNumber=12345).status_code == 200

    def test_summary_holdings_get_no_oclcNumber_passed(self, stub_session):
        with pytest.raises(TypeError):
            stub_session.summary_holdings_get(holdingsAllVariantRecords=True)

    @pytest.mark.http_code(200)
    def test_summary_holdings_search(self, stub_session, mock_session_response):
        assert stub_session.summary_holdings_search(oclcNumber=12345).status_code == 200

    def test_summary_holdings_search_invalid_oclc_number(self, stub_session):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.summary_holdings_search(oclcNumber="odn12345")
        assert msg in str(exc.value)

    @pytest.mark.http_code(200)
    def test_shared_print_holdings_search(self, stub_session, mock_session_response):
        assert (
            stub_session.shared_print_holdings_search(oclcNumber=12345).status_code
            == 200
        )

    def test_shared_print_holdings_search_with_invalid_oclc_number_passed(
        self, stub_session
    ):
        msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            stub_session.shared_print_holdings_search(oclcNumber="odn12345")
        assert msg in str(exc.value)
