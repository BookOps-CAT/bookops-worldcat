
# Advanced Usage

## OCLC Number Formatting
`MetadataSession` accepts OCLC numbers in methods' arguments as integers or strings with or without a prefix (eg. "ocm", "ocn", or "on"). The following are all acceptable:

```python title="Acceptable oclcNumber arguments"
session.brief_bibs_get(oclcNumber="ocm00012345")
session.brief_bibs_search(oclcNumber="00054321")
session.bib_get_classification(oclcNumber=12121)
```
The `bib_get_current_oclc_number` and `holdings_get_current` methods accept multiple OCLC Numbers passed to the `oclcNumbers` argument. For these methods OCLC Numbers can be passed as a list of strings and/or integers or a string with the numbers separated by commas. The following are all acceptable:

```python title="Acceptable oclcNumbers arguments"
session.holdings_get_current(oclcNumbers=["ocm00012345", "00012346", "12347"])
session.holdings_get_current(oclcNumbers=["ocm00012345", "00012346", 12347])
session.bib_get_current_oclc_number(oclcNumbers="ocm00012345, 00012346, 12347")
```

## Authentication
### WorldcatAccessToken
A `WorldcatAccessToken` object retains the underlying Requests object functionality ([`requests.Request`](https://requests.readthedocs.io/en/latest/api/#requests.request)) which can be accessed via the `.server_response` attribute:

```python title="Obtaining an Access Token"
from bookops_worldcat import WorldcatAccessToken

token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
    agent="my_app/version 1.0.0"
)
print(token.server_response.status_code)
#>200
print(token.server_response.elapsed):
#>0:00:00.650108
```
Detailed information can be accessed using the `.json()` method.
```{ .json title="token.server_response.json()" .no-copy}
{
  "access_token": "tk_TokenString", 
  "expires_at": "2024-03-14 19:52:37Z", 
  "authenticating_institution_id": "00001", 
  "principalID": "", 
  "context_institution_id": "00001", 
  "scopes": "WorldCatMetadataAPI:view_brief_bib",
  "token_type": "bearer", 
  "expires_in": 1199, 
  "principalIDNS": ""
}
```
Users can check if the token has expired by calling the `is_expired` method:
```python title="token.is_expired()"
print(token.is_expired())
#>False
```
A failed token request raises a `WorldcatAuthorizationError` which provides the error code and detailed message returned by the server.

```python title="WorldcatAuthorizationError"
from bookops_worldcat import WorldcatAccessToken

token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="MetadataAPI",
    agent="my_app/version 1.0.0"
)
print(token)
#>bookops_worldcat.errors.WorldcatAuthorizationError: b'{"code":403,"message":"Invalid scope(s): MetadataAPI (MetadataAPI) [Invalid service specified, Not on key]"}'
```

#### Identifying your institution
Though uncommon, users can request that OCLC set up their WSKeys to allow them to work on behalf of multiple institutions. The user can then authenticate on behalf of any of the institutions associated with that WSKey. 

If your WSKey is set up to work on behalf of multiple institutions, you can identify your institution when initiating a `WorldcatAccessToken` object. Pass the Registry ID for the institution you wish to work on behalf of to the scopes parameter as context.

```python title="Access Token with Context"
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI context:00001",
    agent="my_app/1.0.0"
)
```

### MetadataSession
#### Event hooks
`MetadataSession` methods support [Requests event hooks](https://requests.readthedocs.io/en/latest/user/advanced/#event-hooks) which can be passed as an argument:

```python title="Event Hooks"
def print_url(response, *args, **kwargs):
    print(response.url)

hooks = {'response': print_url}
session.brief_bibs_get(850939579, hooks=hooks)
#>https://metadata.api.oclc.org/worldcat/search/brief-bibs/850939579
```

#### Identifying your application
BookOps-Worldcat provides a default `user-agent` value in the headers of all requests to OCLC web services: `bookops-worldcat/{version}`. Users are encouraged to update the `user-agent` value to properly identify your application to OCLC servers. This will provide a useful piece of information for OCLC staff if they need to assist with any troubleshooting problems that may arise.

To set a custom `user-agent` in a session simply pass it as an argument when initiating the session:
```python title="Custom user-agent"
session = MetadataSession(authorization=token, agent="my_client_name")
```

Alternatively, users can update the `.headers` attribute after initializing the session:
```python title="Update MetadataSession headers"
session.headers.update({"user-agent": "my-app/version 1.0"})
```

The `user-agent` header can be set for an access token request as well. To do that simply pass it as the `agent` parameter when initiating `WorldcatAccessToken` object:
```python title="WorldcatAccessToken with custom agent"
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
    agent="my_app/1.0.0"
)
```
#### Automatic Token Refresh
All requests made within a `MetadataSession` have a built-in access token auto-refresh feature. While a session is open, the current token will be checked for expiration before sending a request. If the token has expired, a new token will be obtained and the `MetadataSession` will continue to send requests.


#### Retry Failed Requests
Users can configure a `MetadataSession` to automatically retry failed requests. This functionality is customizable with the `totalRetries`, `backoffFactor`, `statusForcelist`, and `allowedMethods` arguments. 

!!! note 
    It is recommended that users only allow for automatic retries on timeouts or other server errors. Users should also =keep their automatic retries as low as possible in order to not overburden the web service. Users should not set up automatic retries for authentication or request errors.

```python title="MetadataSession with Retries"
with MetadataSession(
    authorization=token,
    totalRetries=3,
    backoffFactor=0.1,
    statusForcelist=[500, 502, 503, 504],
    allowedMethods=["GET"],
) as session:
    session.bib_get("12334")
```
Bookops-Worldcat will return a `RetryError` if a request is attempted up to the value of `totalRetries` and still fails.