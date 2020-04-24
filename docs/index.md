# BookOps-Worldcat

[![Build Status](https://travis-ci.com/BookOps-CAT/bookops-worldcat.svg?branch=master)](https://travis-ci.com/BookOps-CAT/bookops-worldcat) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Requires Python 3.7 and up.

Bookops-Worldcat is a Python wrapper around [OCLC's](https://www.oclc.org/en/home.html) [Worldcat](https://www.worldcat.org/) [Search](https://www.oclc.org/developer/develop/web-services/worldcat-search-api.en.html) and [Metadata](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) APIs.  

Bookops-Worldcat simplifies some of the APIs boilerplate and takes advantage of functinality of the [Requests library](https://requests.readthedocs.io/en/master/). The wrapper supports at the moment only OAuth 2.0 endpoints and flows, specifically it uses Client Credential Grant and Access Token.  
Please note, not all functionalities of Worldcat Search and Metadata APIs are implemented because this tool was build for our organization's specific needs. We are open though to collaboration to expand and improve the package.  

[WorldCat Search API](https://www.oclc.org/developer/develop/web-services.en.html) provides developer-level access to WorldCat for bibliographic, holdings and location data. It requires credentials (WSkey only) that can be obtain from OCLC. It allows searching and retrieving bibliographic records for books, videos, music, etc.   
BookOps wrapper offers following operations:  

+ SRU (query in a form of a CQL Search)  
+ Read (retrieves a single bibliographic record by OCLC number)  
+ Lookup By ISBN  
+ Lookup By ISSN
+ Lookup By Standard Number

[Worldcat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html) is a read-write service for WorldCat. It allows to add and update records in WorldCat, mantain holdings, and work with local bibliographic data. Metadata API requires OCLC credentials. BookOps wrapper focuses on following API operations:  

+ Bibliographic Resource  
    + Read (retrieves a single bibliographic record by OCLC number)  
+ Holdings Resource  
    + Set/Create  
    + Unset/Delete  
    + Retrieve Status  
    + Batch Set - Multiple OCLC Numbers
    + Batch Unset - Multiple OCLC Numbers


## Installation

To install use pip:  

`$ pip install bookops-worldcat`  


## Quickstart

#### SearchSession (Search API)

WorldCat Search API requires OCLC's WSkey. See [OCLC authentication docs](https://www.oclc.org/developer/develop/authentication.en.html) for more information how to obtain it. Returned records are by default in MARC XML format. Other formats offered by the API are not currently supported.  

The SearchSession offers following methods to query WorldCat:

+ simple lookups return a single, matching record with highest holdings count in WorldCat:  
    + `lookup_isbn` perorms ISBN search
    + `lookup_issn` performs ISSN search
    + `lookup_oclc_number`  performs OCLC number search
    + `lookup_standard_number`performs standard number query
* advanced query `sru_query` that utilize OCLC various indexes, filters, and sortings

Lookups basic usage:  
```python
>>> from bookops_worldcat import SearchSession

>>> session = SearchSession(credentials="your WSkey")
>>> results = session.lookup_oclc_number("00000000123")
>>> print(results.status_code)
200
```

Using context manager:  
```python
with SearchSession(credentials="your WSkey") as session:
    results = session.lookup_isbn(isbn="9781680502404", service_level='full')
```

`sru_query` offers a flexible way to build complex query that get translated into SRU/CQL syntax. 
`sru_query` query attribute syntax supports Boolean operators:

+ `&` - AND
+ `<>` - NOT
+ `|` - OR

Use parenthesis to encapsulate logic statements.

Advanced CQL query example (keyword search for "civil war" with subject "antietam" or "sharpsburg", results sorted by date from most recent one):  
```python 
with SearchSession(credentials="your WSkey") as session:
    results = session.sru_query(
        query='srw.kw="civil war"&(srw.su="antietam"|srw.su="sharpsburg")',
        maximum_records=50,
        sort_keys=[("date", "descending")],
        service_level="full")
```

#### WorldcatAccessToken

WorldCat Metadata API requires an access token for authorization. This library utilizes OAuth 2.0 and Client Credential Grant flow to aquire OCLC's access token. 

Basic usage:
```python
from bookops_worldcat import WorldcatAccessToken

token = WorldcatAccessToken(
    oauth_server="https://oauth.oclc.org",
    key="your_WSKey",
    secret="your_secret",
    options={
        "scope": ["WorldCatMetadataAPI"],
        "principal_id": "your_principal_id",
        "principlal_idns": "your_principal_idns"
    }
)
print(token.token_str)
"tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
print(token.is_expired())
False
```

Token object retains underlying Requests object functionality (`requests.Request`) that can be accessed via `.server_response` attribute:
```python
print(token.server_response.status_code)
200
print(token.server_response.elapsed):
0:00:00.650108
print(token.server_response.json())
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

#### MetadataSession (Metadata API)

A wrapper around WorldCat Metadata API. MetadataSession inherits `requests.Session` methods. The session is authorized using `WorldcatAccessToken` object. Returned bibliographic records are by default in MARC/XML format (OCLC's native CDF XML and the CDF translation into JSON serializations are not supported at the moment).

Basic usage:
```python
from bookops_worldcat import MetadataSession

with MetadataSession(credentials=token) as session:
    results = session.get_record("00000000123")
```

Returned response is a `requests.Response` object:
```python
print(results.status_code)
200
print(results.url)
"https://worldcat.org/bib/data/00000000123"
```
To avoid any `UnicodeEncodeError` it is recommended to access retrieved data with `.content` attribute of the response object:
```python
print(response.content)
```

MetadataSession supports also various holdings operations:  

+ `holdings_get_status` retrieves holding status of requested record 
+ `holdings_set` sets holdings on an individual bibliographic record
+ `holdings_unset` deletes holdings on an individual bibliographic record
+ `holdings_set_batch` allows to set holdings on multiple records; it is not limited by OCLC 50 bibs limit)
+ `holdings_unset_batch` allows to delete holdings on multiple records and is not limited to OCLC's 50 records restriction

example:  
```python
session.holdings_set(oclc_number="00000000123")
```
pass OCLC record numbers for batch operations as a list of strings:  
```python
session.holdings_unset_batch(
    oclc_numbers=[
        "00000000123",
        "00000000124",
        "00000000125",
        "00000000126"
    ]
)
```

MetadataSession requests support [Requests event hooks](https://requests.readthedocs.io/en/latest/user/advanced/#event-hooks) that can be passes as an argument:
```python
def print_url(response, *args, **kwargs):
    print(response.url)


hooks = {'response': print_url}

session.get_record("00000000123", hooks=hooks)
"https://worldcat.org/bib/data/00000000123"
```
