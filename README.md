[![Build Status](https://github.com/BookOps-CAT/bookops-marc/actions/workflows/unit-tests.yaml/badge.svg?branch=main)](https://github.com/BookOps-CAT/bookops-worldcat/actions) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=main)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=main) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-worldcat

BookOps-Worldcat provides a Python interface for the WorldCat Metadata API. This wrapper simplifies requests to OCLC web services making them more accessible to OCLC member libraries.

Bookops-Worldcat version 1.0 supports changes released in version 2.0 (May 2023) of the OCLC Metadata API. 

## Installation

Use pip:

`$ pip install bookops-worldcat`

## Documentation

For full documentation please see https://bookops-cat.github.io/bookops-worldcat/

## Features

Bookops-Worldcat takes advantage of the functionality of the popular [Requests library](https://requests.readthedocs.io/en/master/) and interactions with OCLC's services are built around 'Requests' sessions. `MetadataSession` inherits all `requests.Session` properties. Server responses are `requests.Response` objects with [all of their properties and methods](https://requests.readthedocs.io/en/master/user/quickstart/#response-content).

Authorizing a web service session simply requires passing an access token to `MetadataSession`. Opening a session allows the user to call specific methods to facilitate communication between the user's script/client and a particular endpoint of the Metadata API. Many of the hurdles related to making valid requests are hidden under the hood of this package, making it as simple as possible.

BookOps-Worldcat supports requests to all endpoints of the WorldCat Metadata API 2.0 and Authentication using the [Client Credential Grant](https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html) flow:

+ [Authentication via Client Credential Grant](https://www.oclc.org/developer/api/keys/oauth/client-credentials-grant.en.html)
+ [Worldcat Metadata API](https://www.oclc.org/developer/api/oclc-apis/worldcat-metadata-api.en.html)
    + Manage Bibliographic Records
    + Manage Institution Holdings
    + Manage Local Bibliographic Data
    + Manage Local Holdings Records
    + Search Member Shared Print Holdings
    + Search Member General Holdings
    + Search Bibliographic Resources
    + Search Local Holdings Resources
    + Search Local Bibliographic Resources

### Basic usage:

Authorizing a MetadataSession
```python
from bookops_worldcat import WorldcatAccessToken
token = WorldcatAccessToken(
    key="my_WSKey",
    secret="my_secret",
    scopes="WorldCatMetadataAPI",
)
print(token)
#>"access_token: 'tk_Yebz4BpEp9dAsghA7KpWx6dYD1OZKWBlHjqW', expires_at: '2024-01-01 12:00:00Z'"
print(token.is_expired())
#>False
>>>session = MetadataSession(authorization=token)
```

Search for brief bibliographic resources
```python
with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(q="ti:The Power Broker AND au: Caro, Robert")
    print(response.json())
```
```json
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
MetadataSession as Context Manager:
```python
with MetadataSession(authorization=token) as session:
    result = session.bib_get("1631862")
    print(result.text) 
```
```xml
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

## Changelog

Consult the [Changelog page](https://bookops-cat.github.io/bookops-worldcat/latest/about/changelog/) for a full list of fixes and enhancements for each version.

## Bugs/Requests

Please use the [Github issue tracker](https://github.com/BookOps-CAT/bookops-worldcat/issues) to submit bugs or request features.

## Contributing

See [Contribution Guidelines]() for information on how to contribute to bookops-worldcat.
