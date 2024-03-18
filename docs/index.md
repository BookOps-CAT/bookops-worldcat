# BookOps-Worldcat

[![Build Status](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=master)](https://github.com/BookOps-CAT/bookops-worldcat/actions) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Bookops-Worldcat is a Python wrapper around [OCLC's](https://www.oclc.org/en/home.html) [WorldCat](https://www.worldcat.org/) [Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html). The package features methods that enable interactions with each endpoint of the API.

The Bookops-Worldcat package simplifies some of the OCLC API boilerplate and ideally lowers the technological threshold for cataloging departments that may not have sufficient programming support to access and utilize the web services. Python, with its gentle learning curve, has the potential to be a perfect vehicle towards this goal.

Bookops-Worldcat version 1.0 supports changes released in version 2.0 (May 2023) of the OCLC Metadata API. 

## Overview

Requires Python 3.8 and up.

Bookops-Worldcat takes advantage of the functionality of the popular [Requests library](https://requests.readthedocs.io/en/master/) and interactions with OCLC's services are built around 'Requests' sessions. `MetadataSession` inherits all `requests.Session` properties. Server responses are `requests.Response` objects with [all of their properties and methods](https://requests.readthedocs.io/en/master/user/quickstart/#response-content).

Authorizing a web service session simply requires passing an access token to `MetadataSession`. Opening a session allows the user to call specific methods to facilitate communication between the user's script/client and a particular endpoint of the Metadata API. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible.

Bookops-Worldcat supports [OAuth 2.0 endpoints and flows](https://www.oclc.org/developer/api/keys/oauth.en.html) and uses the [Client Credential Grant](https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html) flow.

## Installation

Use pip to install:

`$ pip -m install bookops-worldcat`

## Interacting with the Metadata API
Users of the WorldCat Metadata API must have OCLC credentials. A web service key, or [WSKey](https://www.oclc.org/developer/develop/authentication/what-is-a-wskey.en.html), can be obtained via the [OCLC Developer Network](https://platform.worldcat.org/wskey/) site. More information about WSKeys is available on the [OCLC Developer Network site](https://www.oclc.org/developer/develop/authentication/how-to-request-a-wskey.en.html). 


### Authentication
Users can obtain an Access Token by passing credential parameters into the `WorldcatAccessToken` object.

```python
from bookops_worldcat import WorldcatAccessToken
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
)
print(token)
>>>"access_token: 'tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW', expires_at: '2024-01-01 17:19:58Z'"
print(token.is_expired())
>>>False
```
This `WorldcatAccessToken` can be passed directly into a `MetadataSession` to authorize requests to the Metadata API web service:

```python
from bookops_worldcat import MetadataSession
session = MetadataSession(authorization=token)
```

### Search WorldCat
Once the `MetadataSession` is authenticated using the `WorldcatAccessToken` object, users can perform many actions in WorldCat using the Metadata API:

```python title="Brief Bib Search"
with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(q="ti:The Power Broker AND au: Caro, Robert")
    print(response.json())
```

Brief bib resources are returned in JSON format which can be parsed using the `.json()` method.
```json title="Brief Bib json"
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
Full bib records can be retrieved by passing the `bib_get` method an OCLC Number. The response is a `requests.Response` object with all its features:
```python title="Get Full Bib Record"
with MetadataSession(authorization=token) as session:
    result = session.bib_get("321339")
    print(result.status_code) 
    print(result.url)
>>>200
>>>"https://metadata.api.oclc.org/worldcat/manage/bibs/321339"
```
Additional examples are provided under the [Basic Usage](basic.md) and [Advanced](advanced.md) tabs at the top of this page.

## Supported OCLC web services

The [WorldCat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) is a read-write service for WorldCat. It allows users to add and update records in WorldCat; maintain institution holdings; search WorldCat using the full suite of bibliographic record indexes; retrieve MARC records in MARC/XML or MARC21; and work with local bibliographic and holdings data. Access to the Metadata API requires OCLC credentials. The BookOps-Worldcat wrapper supports requests to all endpoints of the WorldCat Metadata API:

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
+ [Manage Local Bibliographic Data](local_data.md)
    + Create local bib data record `/manage/lbds`
    + Retrieve local bib data record `/manage/lbds/{controlNumber}`
    + Replace local bib data record `/manage/lbds/{controlNumber}`
    + Delete local bib data record `/manage/lbds/{controlNumber}`
+ [Manage Local Holdings Records](local_data.md)
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
+ [Search Local Holdings Resources](local_data.md)
    + Search shared print local holdings resources `/search/retained-holdings`
    + Retrieve local holdings resource `/search/my-holdings/{controlNumber}`
    + Search local holdings resources `/search/my-holdings`
    + Browse my local holdings resources `/browse/my-holdings`
+ [Search Local Bibliographic Resources](local_data.md)
    + Retrieve local bibliographic resource `/search/my-local-bib-data/{controlNumber}`
    + Search local bibliographic resources `/search/my-local-bib-data`

## What's new in Bookops-Worldcat 1.0

New functionality available in version 1.0:

+ Send requests to all endpoints of WorldCat Metadata API
    + Match bib records and retrieve bib classification
    + Create, update, and validate bib records
    + Create, retrieve, update, and delete local bib and holdings records
+ Add automatic retries to failed requests
+ Authenticate and authorize for multiple institutions within `MetadataSession`
+ Support for Python 3.11 and 3.12

See the [Changelog page](https://bookops-cat.github.io/bookops-worldcat/latest/changelog/) for a full outline of fixes and enhancements with each version.