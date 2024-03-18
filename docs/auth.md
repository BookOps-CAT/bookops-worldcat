Querying the WorldCat Metadata API is a two step process. Users must first pass their API credentials to the WorldCat Authorization Server to obtain an Access Token. Users can then query the Metadata API using that Access Token.

## Authorization
A Worldcat Access Token can be obtained by passing credential parameters into the `WorldcatAccessToken` object.

```python
>>> from bookops_worldcat import WorldcatAccessToken
>>> token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
)
>>> print(token)
"access_token: 'tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW', expires_at: '2024-01-01 17:19:58Z'"
>>> print(token.is_expired())
False
```

This `token` object can be passed directly into `MetadataSession` to authorize requests to the Metadata API web service:

```python
>>> from bookops_worldcat import MetadataSession
>>> session = MetadataSession(authorization=token)
```

### MetadataSession as Context Manager
A `MetadataSession` can also be used as a context manager. This allows users to use the same parameters and configuration for each request they send to the Metadata API. `MetadataSession` inherits all `requests.Session` methods and properties (see [Advanced Usage > MetadataSession](auth.md#metadatasession)) for more information. 

```python title="Metadata Session as context manager"
with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(q="ti:The Power Broker AND au: Caro, Robert")
    print(response.json())
```

## Advanced Usage
### WorldcatAccessToken
A `WorldcatAccessToken` object retains the underlying Requests object functionality (`requests.Request`) which can be accessed via the `.server_response` attribute:

```python title="Obtaining an Access Token"
from bookops_worldcat import WorldcatAccessToken
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
    agent="my_app/version 1.0.0"
)
```
```python title="Attributes of token.server_response"
print(token.server_response.status_code)
200
print(token.server_response.elapsed):
0:00:00.650108
```
Detailed information can be accessed using the `.json()` method.
```json title="token.server_response.json()"
{
  "access_token": "tk_TokenString", 
  "expires_at": "2024-03-14 19:52:37Z", 
  "authenticating_institution_id": "00001", 
  "principalID": "", 
  "context_institution_id": "00001", 
  "scopes": "WorldCatMetadataAPI:manage_bibs WorldCatMetadataAPI:view_brief_bib WorldCatMetadataAPI:view_retained_holdings WorldCatMetadataAPI:manage_institution_lhrs WorldCatMetadataAPI:manage_institution_holdings WorldCatMetadataAPI:view_summary_holdings WorldCatMetadataAPI:view_my_holdings WorldCatMetadataAPI:view_my_local_bib_data WorldCatMetadataAPI:manage_institution_lbds", 
  "token_type": "bearer", 
  "expires_in": 1199, 
  "principalIDNS": ""
}
```
Users can check if the token has expired by calling the `is_expired` method:
```python title="token.is_expired()"
print(token.is_expired())
False
```
A failed token request raises a `WorldcatAuthorizationError` which provides the error code and detailed message returned by the server.

#### Identifying your institution
Though uncommon, users can request that OCLC set up their WSKey to allow them to work on behalf of multiple institutions. The user can then authenticate on behalf of any of the institutions associated with that WSKey. 

To identify your institution, pass the Registry ID for your institution to the scopes parameter as context when initiating a `WorldcatAccessToken` object

```python title="Access Token Context"
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI context:00001",
    agent="my_app/1.0.0"
)
```

### MetadataSession
`MetadataSession` inherits all `requests.Session` methods. MARC records are returned in MARC/XML format by default for requests sent to any `/manage/lhrs/` or `/manage/lbds/` endpoints, as well as requests made using the `bib_get`, `bib_create` and `bib_replace`. It is possible to receive responses in MARC21 format these endpoints by passing 'application/marc' to the `responseFormat` argument. 

**Method:**
=== "MARC/XML"

    ```py
    response = session.bib_get(850939579)
    print(response)
    ```

=== "MARC21"

    ```py
    response = session.bib_get(850939579, responseFormat="application/marc")
    print(response)
    ```

**Output:**
=== "MARC/XML"

    ```XML
    MARC/XML
    ```

=== "MARC21"

    ```text
    MARC21
    ```

Methods that return brief bibliographic resources or holdings summaries return responses serialized into JSON.

=== "Brief Bib"

    ```json
    brief bib record
    ```

=== "Holdings Summary"

    ```json
    holdings data summary
    ```

#### Event hooks
`MetadataSession` methods support [Requests event hooks](https://requests.readthedocs.io/en/latest/user/advanced/#event-hooks) which can be passed as an argument:

```python
def print_url(response, *args, **kwargs):
    print(response.url)

hooks = {'response': print_url}
session.brief_bibs_get(850939579, hooks=hooks)
```

#### Identifying your application
BookOps-Worldcat provides a default `user-agent` value in the headers of all requests to OCLC web services: `bookops-worldcat/{version}`. Users are encouraged to update the `user-agent` value to properly identify your application to OCLC servers. This will provide a useful piece of information for OCLC staff if they need to assist with any troubleshooting problems that may arise.

To set a custom `user-agent` in a session simply pass is as an argument when initiating the session:
```python title="Custom user-agent"
session = MetadataSession(authorization=token, agent="my_client_name")
```

... or update its `.headers` attribute after initializing the session:
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
#### Auto Refresh and Automatic Retries
All requests made within a `MetadataSession` have a built-in access token auto-refresh feature. While a session is open, the current token will be checked for expiration before sending a request. If the token has expired, a new token will be obtained and the `MetadataSession` will continue to send requests.

It is possible to configure a `MetadataSession` to automatically retry failed requests. This functionality is customizable with the `totalRetries`, `totalRetries`, `statusForcelist`, and `allowedMethods` arguments. 

!!! note 
    It is recommended that users only allow for automatic retries on timeouts or other server errors and keep their automatic retries as low as possible. Users should not set up automatic retries for authentication or request errors.

```python title="MetadataSession with Retries"
with MetadataSession(
    authorization=token,
    totalRetries=3,
    totalRetries=0.1,
    statusForcelist=[500, 502, 503, 504],
    allowedMethods=["GET"],
) as session:
    session.bib_get("12334")
```


