# -*- coding: utf-8 -*-

import pytest

from bookops_worldcat.utils import *
from bookops_worldcat.errors import InvalidOclcNumber


class MockServiceErrorResponse:
    """Simulates error response from the web service"""

    def __init__(self):
        self.status_code = 400
        self.url = "https://test.org/some_endpoint"
        self.text = "{'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}"

    def json(self):
        return {
            "type": "MISSING_QUERY_PARAMETER",
            "title": "Validation Failure",
            "detail": "details here",
        }


class TestUtils:
    """Tests various methods in utils module"""

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclc_number' is missing.",
            ),
            (
                [12345],
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclc_number' is of invalid type.",
            ),
            (
                12345.5,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclc_number' is of invalid type.",
            ),
            (
                "bt12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclc_number' does not look like real OCLC #.",
            ),
            (
                "odn12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclc_number' does not look like real OCLC #.",
            ),
        ],
    )
    def test_verify_oclc_number_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            verify_oclc_number(argm)
            assert msg == str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            ("000012345", 12345),
            (12345, 12345),
            ("ocm00012345", 12345),
            ("ocn00012345", 12345),
            ("ocn12345", 12345),
            (" on12345 \n", 12345),
        ],
    )
    def test_verify_oclc_number_success(self, argm, expectation):
        assert verify_oclc_number(argm) == expectation

    def test_parse_error_response(self):
        response = MockServiceErrorResponse()
        assert (
            parse_error_response(response)
            == "Web service returned 400 error: {'type': 'MISSING_QUERY_PARAMETER', 'title': 'Validation Failure', 'detail': 'details here'}; https://test.org/some_endpoint"
        )
