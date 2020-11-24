# Changelog

## 0.3.1 (11/24/2020)

+ Bug fixes:
    + MetadataSession timeout param correctly passed into requests
    + Fixed auto refreshing of the access token when expired
    + testing: fixed testing for error messages on exceptions & testing of stale tokens

+ Dependencies bump
    + certifi from 2020.6.20 to 2020.11.8
    + requests from 2.24.0 to 2.25.0
    + urlib3 from 1.25.10 to 1.26.2
+ Added Python 3.9 testing to CI


## 0.3.0 (10/03/2020)

+ Introduces multiple breaking changes compared to the previous version!
+ Dropped features related to the WorldCat Search API
+ Support for Worldcat Metadata API v.1.1 introduced in May 2020
+ Supported Metdata API endpoints:
    + /bibs-retained-holdings
    + /bibs-summary-holdings
    + /brief-bibs
    + /brief-bibs/{oclcNumber}
    + /brief-bibs/{oclcNumber}/other-editions
    + /bib/data/{oclcNumber}
    + /bib/checkcontrolnumbers
    + /ih/data (POST|DELETE)
    + /ih/checkholdings
    + /ih/datalist (POST|DELETE)
+ API reference added to docs with mkapi

## 0.2.1 (9/28/2020)

+ added functionality for docs versioning with mike

## 0.2.0 (04/30/2020)

+ Expanded and improved documentation
+ Customizable "user-agent" in session header and token request
+ SRU/CQL query syntax aligned with OCLC specifications
+ `TokenRequestError` exception added on failed access token request
+ fixed hooks info in docstrings in `SearchSession` and `MetadataSession`
