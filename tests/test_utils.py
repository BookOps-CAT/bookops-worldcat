# -*- coding: utf-8 -*-

import pytest

from bookops_worldcat.errors import InvalidOclcNumber
from bookops_worldcat.utils import (
    _str2list,
    prep_oclc_number_str,
    verify_ids,
    verify_oclc_number,
    verify_oclc_numbers,
)


class TestUtils:
    """Tests various methods in utils module"""

    @pytest.mark.parametrize(
        "argm,expectation",
        [
            ("ocm00054321", "54321"),
            ("ocm11111", "11111"),
            ("ocn123456789", "123456789"),
            ("on1234567890", "1234567890"),
            ("on12345678901", "12345678901"),
            (" ocn000111111", "111111"),
            ("00012345", "12345"),
            ("11111", "11111"),
            ("(OCoLC)00012345", "12345"),
            (" (OCoLC)00012349", "12349"),
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
        "argm,expectation",
        [
            ("58122,13437", "58122,13437"),
            ("58122, 13437", "58122,13437"),
            (["58122", 13437], "58122,13437"),
            (["58122", "13437"], "58122,13437"),
            ([58122, 13437], "58122,13437"),
            (58122, "58122"),
            ("58122", "58122"),
            ([58122], "58122"),
            (["58122"], "58122"),
            ("BKL,NYP", "BKL,NYP"),
            ("BKL, NYP", "BKL,NYP"),
            (["BKL", "NYP"], "BKL,NYP"),
            ("BKL", "BKL"),
            (["BKL"], "BKL"),
        ],
    )
    def test_verify_ids(self, argm, expectation):
        assert verify_ids(argm) == expectation

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
            ("00011111", "11111"),
            (12345678901, "12345678901"),
            (2222, "2222"),
            ("ocm00001234", "1234"),
            ("ocm12345678", "12345678"),
            ("ocn123456789", "123456789"),
            (" on1111111111 \n", "1111111111"),
            ("(OCoLC)00012345", "12345"),
            ("(OCoLC)00012345", "12345"),
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
                "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s.",
            ),
            (
                "",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s.",
            ),
            (
                [],
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s.",
            ),
            (
                ",,",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s.",
            ),
            (
                12345.5,
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumbers' must be a single integer, a list or a comma separated string of valid OCLC #s.",
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
            (
                "ocm123456789",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
            (
                "ocn1",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
            (
                "ocn1234567890",
                pytest.raises(InvalidOclcNumber),
                "Argument 'oclcNumber' does not look like real OCLC #.",
            ),
            (
                "on1",
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
            ("1111", ["1111"]),
            ("1111, ocm00002222", ["1111", "2222"]),
            (
                "ocm00012345, ocn123456789, on1234567890, (OCoLC)00067890",
                ["12345", "123456789", "1234567890", "67890"],
            ),
            (123456789, ["123456789"]),
            ([11111, "(OCoLC)00022222"], ["11111", "22222"]),
            (
                [
                    "ocm11111",
                    "ocm10000001",
                    "ocm01111111",
                    "ocn100000001",
                    "on1000000001",
                ],
                ["11111", "10000001", "1111111", "100000001", "1000000001"],
            ),
        ],
    )
    def test_verify_oclc_numbers_parsing(self, argm, expectation):
        assert verify_oclc_numbers(argm) == expectation
