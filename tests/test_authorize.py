import requests

from bookops_worldcat import __version__
from bookops_worldcat.authorize import AuthorizeAccess


def test_mocked_credentials(mock_credentials):
    assert mock_credentials == {
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


class TestAuthorizeAccess:
    """Test AuthorizeAccess and obraining token"""

    def test_access_initiation_via_credentials(
        self, mock_access_initiation_via_credentials, mock_credentials
    ):
        creds = mock_credentials
        access = mock_access_initiation_via_credentials

        assert access.oauth_server == creds["oauth_server"]
        assert access.key == creds["key"]
        assert access.secret == creds["secret"]
        assert access.grant_type == "client_credentials"
        assert access.options == creds["options"]


# def test_token_response(mock_credentials, requests_mock):
#     cred = mock_credentials
#     requests_mock.post(
#         "https://oauth.oclc.test.org/token",
#         headers={"user-agent": f"bookops-worldcat/{__version__}"},
#         auth=(cred["key"], cred["secret"]),
#         data={"grant_type": "client_credentials", "scope": cred["scope"]},
#         timeout=(5, 5),
#         text="OK",
#     )

#     access = AuthorizeAccess(
#         oauth_server=cred["oauth_server"],
#         grant_type="client_credentials",
#         key=cred["key"],
#         secret=cred["secret"],
#         options={
#             "scope": cred["scope"],
#             "authenticating_institution_id": cred["authenticating_institution_id"],
#             "context_institution_id": cred["context_institution_id"],
#         },
#     )

# assert access.get_token.json() == mock_post_token_response
