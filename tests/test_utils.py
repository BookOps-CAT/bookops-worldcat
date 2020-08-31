# -*- coding: utf-8 -*-

import pytest

from bookops_worldcat.utils import *


class TestUtils:
    """Tests various methods in utils module"""

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (None, pytest.raises(TypeError), "Argument 'oclc_number' is missing."),
            (
                12345,
                pytest.raises(TypeError),
                "Argument 'oclc_number' must be a string.",
            ),
            (
                "ocm12345",
                pytest.raises(ValueError),
                "Argument 'oclc_number' must include only digits.",
            ),
        ],
    )
    def test_verify_oclc_number_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            verify_oclc_number(argm)
            assert msg == str(exp.value)

    def test_verify_oclc_number_success(self):
        verify_oclc_number("000012345")
