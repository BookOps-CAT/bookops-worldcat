[![Build Status](https://travis-ci.com/BookOps-CAT/bookops-worldcat.svg?branch=master)](https://travis-ci.com/BookOps-CAT/bookops-worldcat) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-worldcat/badge.svg?branch=master&service=github)](https://coveralls.io/github/BookOps-CAT/bookops-worldcat?branch=master) [![PyPI version](https://badge.fury.io/py/bookops-worldcat.svg)](https://badge.fury.io/py/bookops-worldcat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bookops-worldcat) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)    

# bookops-worldcat  
**EARLY ALPHA VERSION**

BookOps Worldcat Search and Metadata APIs wrappers abstracting OCLC's boilerplate.  
Focus is on selected, relevant to our cataloging department functionality of these APIs.  

### Instalation

Use pip:

`$ pip install bookops-worldcat`


### Features

This package takes advantage of functionality of a popular [Requests library](https://requests.readthedocs.io/en/master/). Interactions with OCLC's services are build around Requests' sessions. Authorizing a session requires simply passing OCLC's WSkey (`SearchSession`) or an access token (`MetadataSession`). Opening a session allows to call its specifc methods that facilitate communication between your script/client and a particular endpoint of OCLC's service. Much of the hurdles related to making valid requests hides under the hood of this package making it as simple as possible.  
Please note, not all functionalities of Worldcat Search and Metadata APIs are implemented because this tool was primarily build for our organization's specific needs. We are open to any collaboration to expand and improve this package.  

BookOps-Worldcat supports at the moment requests to following OCLC's web services:  

+ [WorldCat Search API](https://www.oclc.org/developer/develop/web-services/worldcat-search-api.en.html
)  
    + SRU
    + Read
    + Lookup By ISBN
    + Lookup By ISSN
    + Lookup By Standard Number
+ [Authentication via Client Credential Grant](https://www.oclc.org/developer/develop/authentication/oauth/client-credentials-grant.en.html)
+ [Worldcat Metadata API](https://www.oclc.org/developer/develop/web-services/worldcat-metadata-api.en.html)
    + Read
    + Set/Create
    + Unset/Delete
    + Retrieve Status
    + Batch Set
    + Batch Unset


Basic usage:
```python
>>> from bookops_worldcat import SearchSession
>>> session = SearchSession(credentials="your_WSkey")
>>> results = session.lookup_isbn("9781680502404")
>>> print(results.status_code)
200
>>> print(results.text)
```
```
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
    <datafield ind1=" " ind2=" " tag="250">
      <subfield code="a">First Little, Brown Spark trade paperback edition.</subfield>
    </datafield>
    <datafield ind1=" " ind2="1" tag="264">
      <subfield code="a">New York, NY :</subfield>
      <subfield code="b">Little, Brown Spark,</subfield>
      <subfield code="c">2020</subfield>
      ...
</record>
```


### Documentation

For full documenation please see https://bookops-cat.github.io/bookops-worldcat/

### Changelog

Consult the [Changelog page](https://bookops-cat.github.io/bookops-worldcat/changelog/) for fixes and enhancements of each version. 

### Bugs/Requests  

Please use [Github issue tracker](https://github.com/BookOps-CAT/bookops-worldcat/issues) to submit bugs or request features.