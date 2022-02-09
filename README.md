[![Build Status](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=master)](https://github.com/BookOps-CAT/bookops-worldcat/actions) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-worldcat
**Early ALPHA version**


BookOps-Worldcat provides a Python interface for the WorldCat Metadata API.
This wrapper simplifies requests to OCLC web services making them ideally more accessible to OCLC member libraries.

Due to major changes introduced by OCLC in May 2020, the version 0.3.0 of the wrapper dropped functionality related to WorldCat Search API. New search endopoints of the Metadata API supported in the 0.3.0 version should fill that gap. While WorldCat Metadata API is our primary focus, we plan in the future to expand wrapper's functionality to other related OCLC web services, including the now dropped Search API.  

## Installation

Use pip:

`$ pip install bookops-worldcat`

## Documentation

For full documentation please see https://bookops-cat.github.io/bookops-worldcat/

## Features

This package takes advantage of the functionality of the popular [Requests library](https://requests.readthedocs.io/en/master/). Interactions with [OCLC](https://www.oclc.org/en/home.html)'s services are built around 'Requests' sessions. Authorizing a web service session simply requires passing an access token to `MetadataSession`. Opening a session allows the user to call specific methods to facilitate communication between the user's script/client and particular endpoint of OCLC API service. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible.
Please note, not all endpoints of the Metadata API are implemented at the moment.  This tool was primarily built for the specific needs of BookOps but we are open to collaboration to expand and improve this package.

At the moment, BookOps-Worldcat supports requests to following OCLC's web services:

+ [Authentication via Client Credential Grant](https://www.oclc.org/developer/develop/authentication/oauth/client-credentials-grant.en.html)
+ [Worldcat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html)
    + [Metadata API Search Functionality](https://developer.api.oclc.org/wc-metadata-v1-1)
      + member shared print holdings
      + member general holdings
      + searching bibliographic resources:
        + search brief bibs
        + retrieve specific brief bib
        + retrieve other editions related to a specific bibliographic resource
    + [Metadata API](https://developer.api.oclc.org/wc-metadata)
      + bibliographic records
        + retrieve full bib
        + find current OCLC number
      + holdings
        + set institution holding for a single resource
        + unset institution holding for a single resource
        + retrieve holding status of a single resource
        + set institution holdings for a batch of resources
        + unset institution holdings for a batch of resouces


#### Basic usage:

Obtaining access token
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

Using a context manager:
```python
with MetadataSession(authorization=token) as session:
    results = session.get_full_bib(1143317889)
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

## Changelog

Consult the [Changelog page](https://bookops-cat.github.io/bookops-worldcat/0.3/changelog/) for fixes and enhancements of each version.

## Bugs/Requests

Please use [Github issue tracker](https://github.com/BookOps-CAT/bookops-worldcat/issues) to submit bugs or request features.

## Todo

+ Metadata API:
  + support for local holdings resources endpoints of the search functionality of the Metadata API
  + support for local bibliographic data endpoints
  + support for holdings batch actions for multiple institutions
  + record validation endpoints
  + methods to create and update bibliographic records
