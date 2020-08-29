# -*- coding: utf-8 -*-

import pytest

from bookops_worldcat import MetadataSession


class TestMockedMetadataSession:
    """Tests MetadataSession methods with mocking"""

    def test_base_session_initiation(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert type(session.authorization).__name__ == "WorldcatAccessToken"

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

    def test_url_brief_bib_oclc_number(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_oclc_number(oclc_number="12345")
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345"
            )

    def test_url_brief_bib_other_editions(self, mock_token):
        with MetadataSession(authorization=mock_token) as session:
            assert (
                session._url_brief_bib_other_editions(oclc_number="12345")
                == "https://americas.metadata.api.oclc.org/worldcat/search/v1/brief-bibs/12345/other-editions"
            )

    def test_url_lhr_controlNumber(self, mock_token):
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
