import pytest

import requests

from bookops_worldcat.authorize import AuthorizeAccess


@pytest.fixture()
def mock_credentials():
    return {
        "name": "TestCreds",
        "library": "OCLC",
        "key": "WSkey",
        "secret": "WSsecret",
        "options": {
            "authenticating_institution_id": "123456",
            "context_institution_id": "00001",
            "principal_id": "00000000-111a-222b-333c-4d444444444d",
            "principal_idns": "urn:oclc:platform:00001",
            "scope": ["scope1", "scope2"],
        },
        "oauth_server": "https://oauth.oclc.test.org",
    }


@pytest.fixture()
def mock_access_initiation_via_credentials(mock_credentials):
    cred = mock_credentials
    access = AuthorizeAccess(
        oauth_server=cred["oauth_server"],
        grant_type="client_credentials",
        key=cred["key"],
        secret=cred["secret"],
        options=cred["options"],
    )
    return access
