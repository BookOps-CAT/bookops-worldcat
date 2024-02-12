# -*- coding: utf-8 -*-

import pytest

from bookops_worldcat.utils import (
    _str2list,
    prep_oclc_number_str,
    verify_oclc_number,
    verify_oclc_numbers,
)
from bookops_worldcat.errors import InvalidOclcNumber


class TestUtils:
    """Tests various methods in utils module"""

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            ("ocm00012345", "12345"),
            ("ocn00012346", "12346"),
            ("on000012347", "12347"),
            (" ocm00012348", "12348"),
        ],
    )
    def test_prep_oclc_number_str(self, argm, expectation):
        assert prep_oclc_number_str(argm) == expectation

    def test_prep_oclc_number_str_exception(self):
        err_msg = "Argument 'oclcNumber' does not look like real OCLC #."
        with pytest.raises(InvalidOclcNumber) as exc:
            prep_oclc_number_str("ODN00012345")

        assert err_msg in str(exc.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            ("12345", ["12345"]),
            ("12345,67890", ["12345", "67890"]),
            ("12345, 67890", ["12345", "67890"]),
            (" , ", []),
            ("", []),
        ],
    )
    def test_str2list(self, argm, expectation):
        assert _str2list(argm) == expectation

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' is missing.",
            ),
            (
                [12345],
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' is of invalid type.",
            ),
            (
                12345.5,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' is of invalid type.",
            ),
            (
                "bt12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
            (
                "odn12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
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
            ("000012345", "12345"),
            (12345, "12345"),
            ("ocm00012345", "12345"),
            ("ocn00012345", "12345"),
            ("ocn12345", "12345"),
            (" on12345 \n", "12345"),
        ],
    )
    def test_verify_oclc_number_success(self, argm, expectation):
        assert verify_oclc_number(argm) == expectation

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                None,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s.",
            ),
            (
                "",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s.",
            ),
            (
                [],
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s.",
            ),
            (
                ",,",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s.",
            ),
            (
                12345.5,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a list or comma separated string of valid OCLC #s.",
            ),
            (
                "bt12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
            (
                "odn12345",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
        ],
    )
    def test_verify_oclc_numbers_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            verify_oclc_numbers(argm)
        assert msg == str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            ("12345", ["12345"]),
            ("12345,67890", ["12345", "67890"]),
            ("ocm0012345, ocm67890", ["12345", "67890"]),
            ([12345, 67890], ["12345", "67890"]),
            (["ocn12345", "on67890"], ["12345", "67890"]),
        ],
    )
    def test_verify_oclc_numbers_parsing(self, argm, expectation):
        assert verify_oclc_numbers(argm) == expectation
