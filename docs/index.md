# BookOps-Worldcat

[![Build Status](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=main)](https://github.com/BookOps-CAT/bookops-worldcat/actions) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=main&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=main) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Bookops-Worldcat is a Python wrapper around [OCLC's](https://www.oclc.org/en/home.html) [WorldCat](https://www.worldcat.org/) [Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html). The package features methods that enable interactions with each endpoint of the API.

The Bookops-Worldcat package simplifies some of the OCLC API boilerplate and ideally lowers the technological threshold for cataloging departments that may not have sufficient programming support to access and utilize the web services. Python, with its gentle learning curve, has the potential to be a perfect vehicle towards this goal.

Bookops-Worldcat version 1.0 supports changes released in version 2.0 (May 2023) of the OCLC Metadata API. 

## Overview

Requires Python 3.8 and up.

Bookops-Worldcat takes advantage of the functionality of the popular [Requests library](https://requests.readthedocs.io/) and interactions with OCLC's services are built around 'Requests' sessions. `MetadataSession` inherits all `requests.Session` properties. Server responses are `requests.Response` objects with [all of their properties and methods](https://requests.readthedocs.io/en/latest/user/quickstart/).

Authorizing a web service session simply requires passing an access token to `MetadataSession`. Opening a session allows the user to call specific methods to facilitate communication between the user's script/client and a particular endpoint of the Metadata API. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible.

Bookops-Worldcat supports [OAuth 2.0 endpoints and flows](https://www.oclc.org/developer/api/keys/oauth.en.html) and uses the [Client Credential Grant](https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html) flow.

## Installation

Use pip to install:

`$ pip -m install bookops-worldcat`

## Interacting with the Metadata API
Users of the WorldCat Metadata API must have OCLC credentials. A web service key, or [WSKey](https://www.oclc.org/developer/develop/authentication/what-is-a-wskey.en.html), can be obtained via the [OCLC Developer Network](https://platform.worldcat.org/wskey/) site. More information about WSKeys is available on the [OCLC Developer Network site](https://www.oclc.org/developer/develop/authentication/how-to-request-a-wskey.en.html). 

Querying the WorldCat Metadata API is a two step process. Users first pass their API credentials to the WorldCat Authorization Server to obtain an Access Token and then use that Access Token to query the Metadata API.

### Examples
Users obtain an Access Token by passing credential parameters into the `WorldcatAccessToken` object.

```python title="Authorizing a MetadataSession"
from bookops_worldcat import WorldcatAccessToken, MetadataSession

token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
)
print(token)
#>"access_token: 'tk_O4WFpJuidaaXJmb8wPb7aMSfJdYZg5XC9Ovo', expires_at: '2024-03-20 15:25:32Z'"
print(token.is_expired())
#>False
session = MetadataSession(authorization=token)
print(session.headers)
#> {'User-Agent': 'bookops-worldcat/1.0.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'Authorization': 'Bearer tk_xS0qvZs5j04ewpJeHUqNxQ1Y4LFprOKLw1ek'}
```
Once a `MetadataSession` is authenticated using a `WorldcatAccessToken` object, users can search WorldCat for bibliographic resources. Brief bib resources are returned in JSON format which can be parsed using the `.json()` method.
```python title="Brief Bib Search"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(
        q="ti:The Power Broker AND au: Caro, Robert"
    )
    print(response.json())
```
```{ .json title="Brief Bib JSON Response" .no-copy}
{
  "numberOfRecords": 89,
  "briefRecords": [
    {
      "oclcNumber": "1631862",
      "title": "The power broker : Robert Moses and the fall of New York",
      "creator": "Robert A. Caro",
      "date": "1975",
      "machineReadableDate": "1975",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "PrintBook",
      "edition": "Vintage Books edition",
      "publisher": "Vintage Books",
      "publicationPlace": "New York",
      "isbns": [
        "0394720245",
        "9780394720241"
      ],
      "mergedOclcNumbers": [
        "750986288",
        "979848451",
        "1171296546",
        "1200988349",
        "1200988563",
        "1201968774",
        "1202023560",
        "1222888365",
        "1282059511",
        "1376480175"
      ],
      "catalogingInfo": {
        "catalogingAgency": "DLC",
        "catalogingLanguage": "eng",
        "levelOfCataloging": " ",
        "transcribingAgency": "DLC"
      }
    }
  ]
}
```
Users can retrieve full bib records from WorldCat by passing the `bib_get` method an OCLC Number:
```python title="Get Full Bib Record"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    result = session.bib_get("1631862")
    print(result.text) 
```
```{ .xml title="Full Bib MARCXML Response" .no-copy}
<?xml version='1.0' encoding='UTF-8'?>
  <record xmlns="http://www.loc.gov/MARC21/slim">
    <leader>00000cam a2200000 i 4500</leader>
    <controlfield tag="001">ocm01631862</controlfield>
    <controlfield tag="003">OCoLC</controlfield>
    <controlfield tag="005">20240201163642.4</controlfield>
    <controlfield tag="008">750320t19751974nyuabf   b    001 0beng  </controlfield>
    <datafield tag="010" ind1=" " ind2=" ">
      <subfield code="a">   75009557 </subfield>
    </datafield>
<!--...-->
    <datafield tag="020" ind1=" " ind2=" ">
      <subfield code="a">9780394720241</subfield>
      <subfield code="q">(paperback)</subfield>
<!--...-->
    <datafield tag="100" ind1="1" ind2=" ">
      <subfield code="a">Caro, Robert A.,</subfield>
      <subfield code="e">author.</subfield>
    </datafield>
    <datafield tag="245" ind1="1" ind2="4">
      <subfield code="a">The power broker :</subfield>
      <subfield code="b">Robert Moses and the fall of New York /</subfield>
      <subfield code="c">by Robert A. Caro.</subfield>
    </datafield>
    <datafield tag="246" ind1="3" ind2="0">
      <subfield code="a">Robert Moses and the fall of New York</subfield>
    </datafield>
    <datafield tag="250" ind1=" " ind2=" ">
      <subfield code="a">Vintage Books edition.</subfield>
    </datafield>
    <datafield tag="264" ind1=" " ind2="1">
      <subfield code="a">New York :</subfield>
      <subfield code="b">Vintage Books,</subfield>
      <subfield code="c">1975.</subfield>
    </datafield>
<!--...-->
</record>

```
Additional examples and a full outline of the functionality available in Bookops-Worldcat are available in the [Get Started](start.md) section.

## Supported OCLC web services

The [WorldCat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) is a read-write service for WorldCat. It allows users to add and update records in WorldCat; maintain institution holdings; search WorldCat using the full suite of bibliographic record indexes; retrieve MARC records in MARCXML or MARC21; and work with local bibliographic and holdings data. Access to the Metadata API requires OCLC credentials. The BookOps-Worldcat wrapper supports requests to all endpoints of the WorldCat Metadata API:

+ [Manage Bibliographic Records](manage_bibs.md)
    + Validate bib record `/manage/bibs/validate/{validationLevel}`
    + Get current OCLC number `/manage/bibs/current`
    + Create bib record `/manage/bibs`
    + Retrieve full bib record `/manage/bibs/{oclcNumber}`
    + Replace bib record `/manage/bibs/{oclcNumber}`
    + Find match for a bib record in WorldCat `/manage/bibs/match`
+ [Manage Institution Holdings](manage_holdings.md)
    + Retrieve status of institution holdings `/manage/institution/holdings/current`
    + Set institution holding with OCLC Number `/manage/institution/holdings/set/{oclcNumber}/set`
    + Unset institution holding with OCLC Number `/manage/institution/holdings/unset/{oclcNumber}/unset`
    + Set institution holding with MARC record `/manage/institution/holdings`
    + Unset institution holding with MARC record `/manage/institution/holdings`
    + Retrieve institution holding codes `/manage/institution/holdings/current`
+ [Manage Local Bibliographic Data](local.md)
    + Create local bib data record `/manage/lbds`
    + Retrieve local bib data record `/manage/lbds/{controlNumber}`
    + Replace local bib data record `/manage/lbds/{controlNumber}`
    + Delete local bib data record `/manage/lbds/{controlNumber}`
+ [Manage Local Holdings Records](local.md)
    + Create local holdings record `/manage/lhrs`
    + Retrieve local holdings record `/manage/lhrs/{controlNumber}`
    + Replace local holdings record `/manage/lhrs/{controlNumber}`
    + Delete local holdings record `/manage/lhrs/{controlNumber}`
+ [Search Member Shared Print Holdings](search.md) `/search/bibs-retained-holdings`
+ [Search Member General Holdings](search.md)
    + Get summary of holdings for known items `/search/bibs-summary-holdings`
    + Search and retrieve summary of holdings `/search/summary-holdings`
+ [Search Bibliographic Resources](search.md)
    + Search brief bib resources `/search/brief-bibs`
    + Retrieve specific brief bib resource `/search/brief-bibs/{oclcNumber}`
    + Retrieve other editions related to a particular bib resource `/search/brief-bibs/{oclcNumber}/other-editions`
    + Retrieve classification recommendations for an OCLC Number `/search/classification-bibs/{oclcNumber}`
+ [Search Local Holdings Resources](local.md)
    + Search shared print local holdings resources `/search/retained-holdings`
    + Retrieve local holdings resource `/search/my-holdings/{controlNumber}`
    + Search local holdings resources `/search/my-holdings`
    + Browse my local holdings resources `/browse/my-holdings`
+ [Search Local Bibliographic Resources](local.md)
    + Retrieve local bibliographic resource `/search/my-local-bib-data/{controlNumber}`
    + Search local bibliographic resources `/search/my-local-bib-data`

## What's new in Bookops-Worldcat
See the [Changelog page](changelog.md) for a full outline of fixes and enhancements with each version.

### Features in Version 1.0

New functionality available in version 1.0:

+ Send requests to all endpoints of WorldCat Metadata API
    + Match bib records and retrieve bib classification
    + Create, update, and validate bib records
    + Create, retrieve, update, and delete local bib and holdings records
+ Add automatic retries to failed requests
+ Authenticate and authorize for multiple institutions within `MetadataSession`
+ Support for Python 3.11 and 3.12

### Migration Information
Bookops-Worldcat 1.0 introduces many breaking changes for users of previous versions. Due to a complete refactor of the Metadata API, the methods from Bookops-Worldcat 0.5.0 have been rewritten. Most of the functionality from previous versions of the Metadata API is still available in Version 2.0. For a comparison of the functionality available in Versions 1.0, 1.1, and 2.0 of the Metadata API, see [OCLC's documentation](https://www.oclc.org/developer/api/oclc-apis/worldcat-metadata-api.en.html) and their [functionality comparison table](https://www.oclc.org/content/dam/developer-network/worldcat-metadata-api/worldcat-metadata-api-functionality-comparison.pdf). 

Versions 1.0 and 1.1 of the Metadata API will be sunset after April 30, 2024 at which point tools that rely on Bookops-Worldcat 0.5 will no longer be able to query the Metadata API.


##### Similar functionality, new method names
Certain functionality has been retained from Bookops-Worldcat Version 0.5 but the methods have been renamed. See below for changes:


|Functionality| Bookops-Worldcat 0.5 | Bookops-Worldcat 1.0  |
|-----------| ----------- | ------------ |
|get brief bib resource| `get_brief_bib` | `brief_bibs_get` |
|get full bib record| `get_full_bib` | `bib_get` |
|get current holdings for record| `holding_get_status` | `holdings_get_current` |
|set holdings on a record| `holding_set` | `holdings_set` |
|unset holdings on a record| `holding_unset` | `holdings_unset` |
|search for brief bibs| `search_brief_bibs` | `brief_bibs_search` |
|get other editions of brief bibs| `search_brief_bib_other_editions` |`brief_bibs_get_other_editions` |
|get current oclc number| `search_current_control_numbers` | `bib_get_current_oclc_number` |
|search member holdings| `search_general_holdings` | `summary_holdings_search` |
|search shared print holdings| `search_shared_print_holdings` | `shared_print_holdings_search` |

##### Deprecated functionality
Certain functionality has been deprecated within Version 2.0 of the Metadata API in including the following methods from Bookops-Worldcat 0.5:  

+ `holdings_set` and `holdings_unset`
    + Users are no longer able to set holdings on multiple records in a single request and should instead send separate requests for each record.
+ `holdings_set_multi_institutions` and `holdings_unset_multi_institutions`
    + Users are no longer able to set holdings for multiple institutions with one request.
    + If your WSKey is valid for multiple institutions, see section on [Identifying Your Institution](advanced.md#identifying-your-application) for an explanation of how to pass your RegistryID to the OCLC Authentication Server and obtain an Access Token.




