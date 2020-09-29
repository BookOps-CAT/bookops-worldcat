[![Build Status](https://travis-ci.com/BookOps-CAT/bookops-worldcat.svg?branch=master)](https://travis-ci.com/BookOps-CAT/bookops-worldcat) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-worldcat
**Early ALPHA version**


BookOps-Worldcat provides a Python interface for the WorldCat Metadata API.
This wrapper simplifies requests to this OCLC web services making them more accessible to OCLC member libraries.

Due to major changes introduced by OCLC in May 2020, the version 0.3.0 of the wrapper dropped functionality related to Search API. New search endopoints of the Metadata API supported in the 0.3.0 version should fill that gap. While WorldCat Metadata API is our primary focus, we plan in the future to expand wrapper's functionality to other related OCLC web services.

## Installation

Use pip:

`$ pip install bookops-worldcat`

## Documentation

For full documentation please see https://bookops-cat.github.io/bookops-worldcat/

## Features

This package takes advantage of functionality of a popular [Requests library](https://requests.readthedocs.io/en/master/). Interactions with [OCLC](https://www.oclc.org/en/home.html)'s services are built around Requests' sessions. Authorizing a web service session simply requires passing an access token to `MetadataSession`. Opening a session allows the user to call specific methods to facilitate communication between the user's script/client and a particular endpoint of OCLC's service. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible.
Please note, not all endpoints of the Metadata API are implemented at the moment as this tool was built primarily for the specific needs of BookOps.
We are open to any collaboration to expand and improve this package.

At the moment, BookOps-Worldcat supports requests to following OCLC's web services:

+ [Authentication via Client Credential Grant](https://www.oclc.org/developer/develop/authentication/oauth/client-credentials-grant.en.html)
+ [Worldcat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html)
    + Metadata API Search Functionality
      + member shared print holdings
      + member general holdings
      + searching bibliographic resources:
        + search brief bibs
        + retrieve specific brief bib
        + retrieve other editions related to a particular bibliographic resource
    + Metadata API
      + bibliographic records
        + retrieve full bib
        + find current OCLC number
      + holdings
        + set institution holding for a single resource
        + unset intitution holding for a single resource
        + retrieve holding status of a single resource
        + set intitution holdings for a batch of resources
        + unset institution holdings for a batch of resouces


#### Basic usage:

Obtaining an access token
```python
>>> from bookops_worldcat import WorldcatAccessToken
>>> token = WorldcatAccessToken(
    key="my_WSkey",
    secret="my_WSsecret",
    scopes="selected_scope",
    principal_id="my_principalID",
    principal_idns="my_principalIDNS",
    agent="my_client"
  )
>>> print(token.token_str)
  "tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW"
```

Metadata API
```python
>>> from bookops_worldcat import MetadataSession
>>> session = MetadataSession(authorization=token)
>>> result = session.get_brief_bib(oclcNumber=1143317889)
>>> print(result)
  <Response [200]>
>>> print(result.json())
```
```json
{
  "oclcNumber": "1143317889",
  "title": "Blueprint : the evolutionary origins of a good society",
  "creator": "Nicholas A. Christakis",
  "date": "2020",
  "language": "eng",
  "generalFormat": "Book",
  "specificFormat": "PrintBook",
  "edition": "First Little, Brown Spark trade paperback edition.",
  "publisher": "Little, Brown Spark",
  "catalogingInfo": {
    "catalogingAgency": "NYP",
    "transcribingAgency": "NYP"
  }
}
```

Context manager:
```python
with MetadataSession(authorization=token) as session:
    results = session.get_full_bib(1143317889)
    print(results.text)
```
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<record xmlns="http://www.loc.gov/MARC21/slim">
    <leader>00000cam a2200000 i 4500</leader>
    <controlfield tag="001">1143317889</controlfield>
    <controlfield tag="008">200305t20202019nyuabf   b    001 0 eng c</controlfield>
    <datafield ind1=" " ind2=" " tag="010">
      <subfield code="a">  2018957420</subfield>
    </datafield>
    <datafield ind1=" " ind2=" " tag="020">
      <subfield code="a">9780316230049</subfield>
      <subfield code="q">(pbk.)</subfield>
    </datafield>
    <datafield ind1=" " ind2=" " tag="020">
      <subfield code="a">0316230049</subfield>
    </datafield>
    <datafield ind1="1" ind2=" " tag="100">
      <subfield code="a">Christakis, Nicholas A.,</subfield>
      <subfield code="e">author.</subfield>
    </datafield>
    <datafield ind1="1" ind2="0" tag="245">
      <subfield code="a">Blueprint :</subfield>
      <subfield code="b">the evolutionary origins of a good society /</subfield>
      <subfield code="c">Nicholas A. Christakis.</subfield>
    </datafield>
      ...
</record>
```

## Changelog

Consult the [Changelog page](https://bookops-cat.github.io/bookops-worldcat/changelog/) for fixes and enhancements of each version.

## Bugs/Requests

Please use [Github issue tracker](https://github.com/BookOps-CAT/bookops-worldcat/issues) to submit bugs or request features.

## Todo

+ Metadata API:
  + support for local holdings resouces endpoints of the search functinality of the Metadata API
  + supoort for local bibliographic data endpoints
  + support for holdings batch actions for multiple institutions
  + record validation endpoints
  + methods to create and update bibliographic records

