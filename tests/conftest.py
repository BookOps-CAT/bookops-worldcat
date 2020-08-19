# -*- coding: utf-8 -*-


import pytest


@pytest.fixture
def mock_credentials():
    return {
        "name": "TestCreds",
        "library": "OCLC",
        "key": "WSkey",
        "secret": "WSsecret",
        "authenticating_institution_id": "123456",
        "context_institution_id": "00001",
        "principal_id": "00000000-111a-222b-333c-4d444444444d",
        "principal_idns": "urn:oclc:platform:00001",
        "scope": ["scope1", "scope2"],
        "oauth_server": "https://oauth.oclc.org.test",
    }
