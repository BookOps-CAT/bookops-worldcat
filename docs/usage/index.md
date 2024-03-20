# Get Started
The first step for accessing the OCLC Metadata API is to authenticate against OCLC's Authorization Server and obtain an Access Token.
### Authentication and Authorization
A Worldcat Access Token can be obtained by passing credential parameters into the `WorldcatAccessToken` object.

```python title="Get Access Token"
from bookops_worldcat import WorldcatAccessToken
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
)
print(token)
#>"access_token: 'tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW', expires_at: '2024-01-01 17:19:58Z'"
print(token.is_expired())
#>False
```

This `token` object can be passed directly into `MetadataSession` to authorize requests to the Metadata API web service:

```python title="Open MetadataSession"
from bookops_worldcat import MetadataSession
session = MetadataSession(authorization=token)
session.brief_bibs_get("321339")
```

### MetadataSession as Context Manager
A `MetadataSession` can also be used as a context manager. This allows users to use the same parameters and configuration for each request they send to the Metadata API and to ensure that the session is closed. `MetadataSession` inherits all `requests.Session` methods and properties (see [Advanced Usage > MetadataSession](advanced.md#metadatasession) for more information). 

```python title="Metadata Session as Context Manager"
with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_get("321339")
```
A `MetadataSession` contains methods that allow users to interact with all of the endpoints of the OCLC Metadata API. See the tabs on the left of this page for more information about `MetadataSession` methods and examples of their usage.