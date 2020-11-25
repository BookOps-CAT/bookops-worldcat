# BookOps-Worldcat

[![Build Status](https://travis-ci.com/BookOps-CAT/bookops-worldcat.svg?branch=master)](https://travis-ci.com/BookOps-CAT/bookops-worldcat) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Requires Python 3.7 and up.

Bookops-Worldcat is a Python wrapper around [OCLC's](https://www.oclc.org/en/home.html) [Worldcat](https://www.worldcat.org/) [Metadata](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) API which supports changes released in the version 1.1 (May 2020) of the web service. The package features methods that utilize [search functionality](https://developer.api.oclc.org/wc-metadata-v1-1) of the API as well as [read-write endpoints](https://developer.api.oclc.org/wc-metadata).

The Bookops-Worldcat package simplifies some of the OCLC API boilerplate, and ideally lowers the technological threshold for cataloging departments that may not have sufficient programming support to access and utilize those web services. Python language, with its gentle learning curve, has the potential to be a perfect vehicle towards this goal.


This package takes advantage of the functionality of the popular [Requests library](https://requests.readthedocs.io/en/master/). Interaction with OCLC's services is built around Requests sessions. `MetadataSession` inherits all `requests.Session` properties. Returned server responses are `requests.Response` objects with [all of their properties and methods](https://requests.readthedocs.io/en/master/user/quickstart/#response-content).

Authorizing a session simply requires passing an access token into `MetadataSession`. Opening a session allows the user to call specific methods which facilitate communication between the user's script/client and a particular endpoint of OCLC's service. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible to access the functionalities of OCLC APIs.
Please note, not all features of the Metadata API are implemented because this tool was primarily built for our organization's specific needs. However, we are open to any collaboration to expand and improve the package.


**Supported OCLC web services:**

At the moment, the wrapper supports only [OAuth 2.0 endpoints and flows](https://www.oclc.org/developer/develop/authentication/oauth.en.html). The specific protocols are [Client Credential Grant](https://www.oclc.org/developer/develop/authentication/oauth/client-credentials-grant.en.html) and [Access Token](https://www.oclc.org/developer/develop/authentication/access-tokens.en.html) for authorization.

[Worldcat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) is a read-write service for WorldCat. It allows adding and updating records in WorldCat, maintaining holdings, and working with local bibliographic data. Access to Metadata API requires OCLC credentials. The BookOps wrapper focuses on the following API operations:

+ Search functionality
    + Find member shared print holdings (`/bibs-retained-holdings`)
    + Get summary of holdings for known items (`/bibs-summary-holdings`)
    + Brief bibliographic resources:
        + Search brief bibliographic resources (`/brief-bibs`)
        + Retrieve specific brief bibliographic resource (`/brief-bibs/{oclcNumber}`)
        + Retrieve other editions related to a particular bibliographic resource (`/brief-bibs/{oclcNumber}/other-edtions`)
+ Full bibliographic resources
    + Retrieve full bibliographic record (`/bib-data`)
    + Get current OCLC number (`/bib/checkcontrolnumber`)
+ Holdings
    + Set and unset institution holding  (`/ih/data`)
    + Retrieve status of institution holdings (`/ih/checkholdings`)
    + Set and unset institution holdings for a batch or records (`/ih/datalist`)


## Installation

To install use pip:

`$ pip install bookops-worldcat`


## Quickstart

Worldcat Metadata API requires OCLC credentials which can be obtained at the [OCLC Developer Network](https://www.oclc.org/developer/home.en.html) site.

#### Obtaining Access Token

The Worldcat access token can be obtained by passing credential parameters into the `WorldcatAccessToken` object.

```python
>>> from bookops_worldcat import WorldcatAccessToken
>>> token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes=["WorldCatMetadataAPI"],
    principal_id="my_principal_id",
    principlal_idns="my_principal_idns"
)
>>> print(token.token_str)
"tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
>>> print(token.is_expired())
False
```

Created `token` object can be directly passed into `MetadataSession` to authorize requests to the Metadata API web service:

```Python
>>> from bookops_worldcat import MetadataSession
>>> session = MetadataSession(authorization=token)
```

#### Searching Brief Bibliographic Records Using Metadata API

The `MetadataSession` is authenticated using the `WorldcatAccessToken` object. The session allows searching brief records as well as retrieving full bibs in the MARC XML format.

Basic usage:
```python
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    results = session.search_brief_bibs(q="ti:zendegi AND au:greg egan")
    print(results.json())
```

Returned brief bibliographic records are in the JSON format that can be parsed via `.json()` method.

```json
{
    "numberOfRecords": 24,
    "briefRecords": [
        {
            "oclcNumber": "430840771",
            "title": "Zendegi",
            "creator": "Greg Egan",
            "date": "2010",
            "language": "eng",
            "generalFormat": "Book",
            "specificFormat": "PrintBook",
            "edition": "First edition.",
            "publisher": "Night Shade Books",
            "mergedOclcNumbers": [
                "664026825"
            ],
            "catalogingInfo": {
                "catalogingAgency": "BTCTA",
                "transcribingAgency": "DLC"
            }
        },
        {
            "oclcNumber": "961162511",
            "title": "Zendegi",
            "creator": "Greg Egan",
            "date": "2013",
            "language": "eng",
            "generalFormat": "AudioBook",
            "specificFormat": "CD",
            "publisher": "Audible Studios on Brilliance Audio",
            "mergedOclcNumbers": [
                "947806980"
            ],
            "catalogingInfo": {
                "catalogingAgency": "AU@",
                "transcribingAgency": "AU@"
            }
        },
    ]
}
```

#### Retrieving Full Bibliographic Records

To retrieve a full bibliographic record from WorldCat use the `.get_full_bib` method. The server returns records in MARC XML format by default.

```python
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    results = session.get_full_bib(oclcNumber=430840771)
    print(results.text)
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <content type="application/xml">
    <response xmlns="http://worldcat.org/rb" mimeType="application/vnd.oclc.marc21+xml">
      <record xmlns="http://www.loc.gov/MARC21/slim">
        <leader>00000cam a2200000 i 4500</leader>
        <controlfield tag="001">on1143317889</controlfield>
        <controlfield tag="003">OCoLC</controlfield>
        <controlfield tag="005">20200328101446.1</controlfield>
        <controlfield tag="008">200305t20202019nyuabf   b    001 0 eng c</controlfield>
        <datafield tag="010" ind1=" " ind2=" ">
          <subfield code="a">  2018957420</subfield>
    </datafield>
        <datafield tag="040" ind1=" " ind2=" ">
          <subfield code="a">NYP</subfield>
          <subfield code="b">eng</subfield>
          <subfield code="e">rda</subfield>
          <subfield code="c">NYP</subfield>
<!--...-->
        <datafield tag="020" ind1=" " ind2=" ">
          <subfield code="a">9780316230049</subfield>
          <subfield code="q">(pbk.)</subfield>
<!--...-->
        <datafield tag="100" ind1="1" ind2=" ">
          <subfield code="a">Christakis, Nicholas A.,</subfield>
          <subfield code="e">author.</subfield>
    </datafield>
        <datafield tag="245" ind1="1" ind2="0">
          <subfield code="a">Blueprint :</subfield>
          <subfield code="b">the evolutionary origins of a good society /</subfield>
          <subfield code="c">Nicholas A. Christakis.</subfield>
    </datafield>
        <datafield tag="250" ind1=" " ind2=" ">
          <subfield code="a">First Little, Brown Spark trade paperback edition.</subfield>
    </datafield>
        <datafield tag="264" ind1=" " ind2="1">
          <subfield code="a">New York, NY :</subfield>
          <subfield code="b">Little, Brown Spark,</subfield>
          <subfield code="c">2020</subfield>
    </datafield>
<!--...-->
  </record>
    </response>
  </content>
  <id>http://worldcat.org/oclc/1143317889</id>
  <link href="http://worldcat.org/oclc/1143317889"></link>
</entry>
```

#### Updating Holdings

`MetadataSession` can be used to check or set/unset your library holdings on a master record in Worldcat:

example:
```python
result = session.holding_set(oclc_number="850939579")
print(result)
<Response [201]>
```

```python
result = session.holding_get_status("850939579")
print(result.json())
```
```json
{
  "title": "850939579",
  "content": {
    "requestedOclcNumber": "850939579",
    "currentOclcNumber": "850939579",
    "institution": "NYP",
    "holdingCurrentlySet": true,
    "id": "http://worldcat.org/oclc/850939579"
  },
  "updated": "2020-10-01T04:10:13.017Z"
}
```

For holdings operations on batches of records see [Advanced Usage>MetadataSession>Updating Holdings](https://bookops-cat.github.io/bookops-worldcat/#holdings)

## Advanced Usage

**Identifying your application**

BookOps-Worldcat provides a default `user-agent` value in headers of all requests to OCLC web services: `bookops-worldcat/{version}`. It is encouraged to update the `user-agent` value to properly identify your application to OCLC servers. This will provide a useful piece of information for OCLC staff if they need to assist with troubleshooting problems that may arise.
To set a custom "user-agent" in a session simply pass is as an argument when initiating the session:
```python
session = MetadataSession(authorization=token, agent="my_client_name")
```

... or simply update its headers attribute:
```python
session.headers.update({"user-agent": "my-app/version 1.0"})
```

The `user-agent` header can be set for an access token request as well. To do that simply pass it as the `agent` parameter when initiating `WorldcatAccessToken` object:
```python
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes=["WorldCatMetadataAPI"],
    principal_id="my_principal_id",
    principlal_idns="my_principal_idns",
    agent="my_app/1.0.0"
)
```

**Event hooks**

`MetadataSession` methods support [Requests event hooks](https://requests.readthedocs.io/en/latest/user/advanced/#event-hooks) which can be passed as an argument:

```python
def print_url(response, *args, **kwargs):
    print(response.url)

hooks = {'response': print_url}
session.get_brief_bib(850939579, hooks=hooks)
```

#### WorldcatAccessToken

Bookops-Worldcat utilizes OAuth 2.0 and Client Credential Grant flow to acquire Access Token. Please note, your OCLC credentials must allow access to the Metadata API in their scope to be permitted to make requests to the web service.

Obtaining:
```python
from bookops_worldcat import WorldcatAccessToken
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes=["WorldCatMetadataAPI"],
    principal_id="my_principal_id",
    principlal_idns="my_principal_idns",
    agent="my_app/version 1.0"
)
```

Token object retains underlying Requests object functionality (`requests.Request`) that can be accessed via the `.server_response` attribute:

```python
print(token.server_response.status_code)
200
print(token.server_response.elapsed):
0:00:00.650108
print(token.server_response.json())
```
```json
{
"user-agent": "bookops-worldcat/0.1.0",
"Accept-Encoding": "gzip, deflate",
"Accept": "application/json",
"Connection": "keep-alive",
"Content-Length": "67",
"Content-Type": "application/x-www-form-urlencoded",
"Authorization": "Basic encoded_authorization_here="
}
```

Checking if the token has expired can be done by calling the `is_expired` method:
```python
print(token.is_expired())
True
```

A failed token request raises `WorldcatAuthorizationError` which provides a returned by the server error code and detailed message.

#### MetadataSession

A wrapper around WorldCat Metadata API. `MetadataSession` inherits `requests.Session` methods.
Returned full bibliographic records are by default in MARC/XML format, but it is possible to receive OCLC's native CDF XML and the CDF translation into JSON serializations by supplying appropriate values in the `response_format` argument to the `get_full_bib` method. Search endpoints of the Metadata API return responses serialized into JSON format only.
All `MetadataSession` issued requests have a build-in access token auto-refresh feature. While a session is open, before any request is sent, a current token is checked for expiration and if needed a new access token is automatically obtained. 


**OCLC numbers in methods' arguments**

`MetadataSession` accepts OCLC numbers in methods' arguments as integers or strings with or without a prefix ("ocm", "ocn", "on"). The following are all acceptable:
```python
session.get_brief_bib(oclcNumber="ocm00012345")
session.get_brief_bib(oclcNumber="00012345")
session.get_brief_bib(oclcNumber=12345)
session.search_current_control_numbers(oclcNumbers=["ocm00012345", "00012346", 12347])
```

##### Search Functionality

MetadataSession supports the following search functionality:

+ `get_brief_bib` retrieves a specific brief bibliographic resource
+ `search_brief_bib_other_editions` retrieves other editions related to a bibliographic resource specified with an OCLC #
+ `search_brief_bibs` retrieves brief resouces for a keyword or a fielded query
+ `search_current_control_numbers` retrieves current OCLC control numbers
+ `search_general_holdings` retrieves a summary of holdings for a specified item
+ `search_shared_print_holdings` finds member library holdings with a commitment to retain (Shared Print)


The server responses are returned in JSON format by default.

**Obtaining brief record**

```python
with MetadataSession(authorization=token) as session:
    result = session.get_brief_bib(850940548)
    print(results.json())
```
```json
{
    "oclcNumber": "850940548",
    "title": "Record Builder Added This Test Record On 06/26/2013 13:07:06.",
    "creator": "OCLC RecordBuilder.",
    "date": "2012",
    "language": "eng",
    "generalFormat": "Book",
    "specificFormat": "PrintBook",
    "catalogingInfo": {
        "catalogingAgency": "OCPSB",
        "transcribingAgency": "OCPSB"
    }
}
```

**Quering WorldCat**

Metadata API provides quite robust methods to query WorldCat. In addition to a flexible query string that supports keyword and fielded searches, it is possibile to set further limits using various elements such as type of item, language, publishing date, etc. It is possible to specify the order of returned records by using the `orderBy` argument. Results are returned as brief records in JSON format.

The query syntax is case-insensitive and allows keyword and phrase search (use quotation marks), boolean operators (AND, OR, NOT), wildcards (# - single character, ? - any number of additional characters), and truncation (use \* character).


keyword search with item type, language, and publishing date limiters:
```python
session.search_brief_bibs(
    q="czarne oceany dukaj",
    itemType="book",
    inLanguage="pol",
    datePublished="2015-2020"
    orderBy="publicationDateDesc"
)
```

fielded query:
```python
session.search_brief_bibs(
    q='ti="czarne oceany" AND au:jacek dukaj AND ge="science fiction"')
```

More about the query syntax can be found in [OCLC documentation](https://www.oclc.org/developer/develop/worldshare-platform/architecture/query-syntax.en.html)


##### Obtaining Full Bibliographic Records

`session.get_full_bib()` method with OCLC number as an argument sends a request for a matching full bibliographic record in WorldCat. The Metadata API correctly matches requested OCLC numbers of records that have been merged together by returning the current master record. By default `get_full_bib` returns records in MARC XML format.

Returned response is a `requests.Response` object with all its features:
```python
with MetadataSession(authorization=token) as session:
    result = session.get_full_bib("00000000123")
    print(result.status_code)
    print(result.url)
200
"https://worldcat.org/bib/data/00000000123"
```
To avoid any `UnicodeEncodeError` it is recommended to access retrieved data with `.content` attribute of the response object:
```python
print(response.content)
```

##### Retrieving Current OCLC Number

`MetadataSession.search_current_control_numbers` method allows retrieval of a current control number of the master record in WorldCat. Occasionally, records identified as duplicates in WorldCat have been merged.  In that case a local control number may not correctly refer to an OCLC master record. Returned responses are in JSON format by default, but it's possible to pass `'application/atom+xml'` in the `response_format` argument to have the response serialized into xml.

`search_current_control_numbers` method accepts control numbers as a list or a comma separated string:
```python
session.search_current_control_numbers(oclcNumbers="00012345,00012346,00012347")
session.search_current_control_numbers(oclcNumbers=[12345, 12346, 12347], response_format="application/atom+xml")
```

##### Holdings

`MetadataSession` supports the following holdings operations:

+ `holding_get_status` retrieves holding status of a requested record
+ `holding_set` sets holding on an individual bibliographic record
+ `holding_unset` deletes holding on an individual bibliographic record
+ `holdings_set` allows holdings to be set on multiple records, and is not limited by OCLC's 50 bib record limit
+ `holdings_unset` allows holdings to be deleted on multiple records, and is not limited to OCLC's 50 bib record restriction

By default, responses are returned in `atom+json` format, but `atom+xml` can be specified:
```python
result = session.holding_get_status(oclcNumber="ocn123456789", response_format="application/atom+xml")
print(result.text)
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">1143317889</title>
  <updated>2020-04-25T05:21:10.233Z</updated>
  <content type="application/xml">
    <holdings xmlns="http://worldcat.org/metadata-api-service">
      <requestedOclcNumber>1143317889</requestedOclcNumber>
      <currentOclcNumber>1143317889</currentOclcNumber>
      <institution>NYP</institution>
      <holdingCurrentlySet>true</holdingCurrentlySet>
      <id>http://worldcat.org/oclc/1143317889</id>
    </holdings>
  </content>
</entry>
```

Pass OCLC record numbers for batch operations as a list of strings or integers or comma separated string with or without a prefix:
```python
session.holdings_set(
    oclcNumbers="00000000123,00000000124,00000000125,00000000126")

session.holdings_unset(oclcNumbers=[123, 124, 125, 126])
```
The OCLC web service limits the number of records in a batch operation to 50, but `MetadataSession` permits larger batches by splitting the batch into chunks of 50 and automatically issuing multiple requests. The return object is a list of returned from server responses.

```python
results = session.holdings_unset(oclcNumbers=[123, 124, 125, 126])

# print results of each batch of 50s
for r in results:
    print(r.json())
```

## Examples

Complex search query:
```python
from bookops_worldcat import WorldcatAccessToken, MetadataSession

# obtain access token
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes=["WorldCatMetadataAPI"],
    principal_id="my_principal_id",
    principal_idns="my_principal_idns",
    agent="my_app/version 1.0"
)


with MetadataSession(authorization=token) as session:

    # search Worlcat
    response = session.search_brief_bibs(
        q="su:civil war AND (su:antietam OR su:sharpsburg)",
        datePublished="2000-2020",
        inLanguage="eng",
        inCatalogLanguage="eng",
        catalogSource="dlc",
        itemType="book",
        itemSubType="digital",
        orderBy="mostWidelyHeld",
        limit=20)
    first_bib = response.json()["briefRecords"][0]
    first_bib_number = first_bib["oclcNumber"]

    # get full bib
    response = session.get_full_bib(oclcNumber=first_bib_number)
    print(response.content)
```

