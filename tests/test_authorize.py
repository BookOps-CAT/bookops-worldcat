import pytest


from bookops_worldcat.authorize import WorldcatAccessToken


class TestWorldcatAccessToken:
    """Tests WorldcatAccessToken object"""

    @pytest.mark.parametrize(
        "argm,expectation, msg",
        [
            (None, pytest.raises(ValueError), "Argument 'key' is required."),
            ("", pytest.raises(ValueError), "Argument 'key' is required."),
            (124, pytest.raises(TypeError), "Argument 'key' must be a string."),
        ],
    )
    def test_key_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            WorldcatAccessToken(key=argm, secret="my_secret", scope=["scope1"])
            assert msg in str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (None, pytest.raises(ValueError), "Argument 'secret' is required."),
            ("", pytest.raises(ValueError), "Argument 'secret' is required."),
            (123, pytest.raises(TypeError), "Argument 'secret' must be a string."),
        ],
    )
    def test_secret_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            WorldcatAccessToken(key="my_key", secret=argm, scope=["scope1"])
            assert msg in str(exp.value)

    @pytest.mark.parametrize(
        "argm,expectation,msg",
        [
            (
                5,
                pytest.raises(TypeError),
                "Argument 'timeout' must be a tuple of two ints or floats.",
            ),
            (
                (None, "abc"),
                pytest.raises(TypeError),
                "Values of 'timeout' tuple must be ints or floats.",
            ),
        ],
    )
    def test_timeout_exceptions(self, argm, expectation, msg):
        with expectation as exp:
            WorldcatAccessToken(
                key="my_key", secret="my_secret", scope=["scope1"], timeout=argm
            )
            assert msg in str(exp.value)
