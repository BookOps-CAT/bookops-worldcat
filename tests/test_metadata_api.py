# -*- coding: utf-8 -*-

import pytest


from bookops_worldcat.metadata_api import MetadataSession


class InvalidToken:
    def __init__(self):
        self.token_str = "fake_token_string"
        self.key = "fake_key"


class TestMetadataSession:
    """Worldcat MetadataSession tests"""

    def test_invalid_token_object_in_argument(self):
        token = InvalidToken()
        with pytest.raises(TypeError):
            assert MetadataSession(credentials=token)

    def test_invalid_token_str_argument(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        token.token_str = None
        with pytest.raises(TypeError):
            assert MetadataSession(credentials=token)

    def test_base_url(self, mock_token_initiation_via_credentials):
        token = mock_token_initiation_via_credentials
        session = MetadataSession(credentials=token)
        assert session.base_url == "https://worldcat.org/"
