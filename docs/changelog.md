# Changelog

## [1.0.0] - (3/5/2024)
### Added


### Changed


### Fixed


## [0.5.0] - (3/11/2022)
### Added
+ feature to set and unset holdings for individual record for multiple institutions (/ih/institutionlist endpoint)
+ `__repr__` method to `WorldcatAccessToken` object

### Changed
+ "refreshing" of access tokens moved to `_session.WorldcatSession` from `metadata_api.MetadataSession` to allow inheritance of this functionality by future clients
+ refactors some of tests

## [0.4.1] - (2/10/2022) 
### Fixed
+ Handling of unexpected 206 HTTP code that is occasionally returned by the MetadataAPI /brief-bibs endpoint

### Changed
+ Introduced a breaking change to exceptions raised on calls to the web service for bibliographic resources: `WorldcatSessionError` was changed to `WorldcatRequestError`. 
+ Dev dependencies updates (pytest, pytest-cov, pytest-mock, mkdocs, black, mik, mkapi, mypy)

### Changed
+ requests to OCLC services are now handled by a new `query.Query` class
+ dependencies update
    + requests to 2.27.1
    + dev dependencies

## [0.4.0] - (6/22/2021)
### Changed
+ Changes to `MetadataSession.search_brief_bibs` method due to /brief-bibs endpoint changes:
    + removed deprecated argument `heldBy`
    + added `groupVariantRecord` and `preferredLanguage` argument
    + modified `groupRelatedEditions` to allow boolean arguments
+ Changes to `MetadataSession.search_general_holdings` method due to API changes:
    + added following arguments: `holdingsAllVariantRecords`, `preferredLanguage`
    + removed deprecated `heldBy` argument
+ Changes to `MetadataSession.search_brief_bib_other_editions`:
    + added `deweyNumber`, `datePublished`, `heldByGroup`, `heldBySymbol`, 
    `heldByInstitutionId`, `inLanguage`, `inCatalogLanguage`, `materialType`, 
    `catalogSource`, `itemType`, `itemSubType`, `retentionCommitments`, 
    `spProgram`, `topic`, `subtopic`, `audience`, `content`, `openAccess`, 
    `peerReviewed`, `facets`, `groupVariantRecords`, `preferredLanguage`, 
    and `orderBy`. 

## [0.3.5] - (6/2/2021)
### Changed
+ Dependencies update
    + urllib3 from 1.26.4 to 1.26.5

## [0.3.4] - (3/22/2021)
### Changed
+ Dependencies update
    + certifi to 2020.12.5
    + chardet to 4.0.0
    + requests to 2.25.1
    + urllib3 to 1.26.4

## [0.3.3] - (12/28/2020)
### Added
+ Type hints
+ Default timeout in the MetadataSession extended to 5 seconds

### Changed
+ Dependencies:
    + pytest bump to 6.1.2
    + mypy 0.7.8

## [0.3.2] - (11/25/2020)
### Fixed
+ MetadataSession timeout parameter correctly passed into every session request


## [0.3.1] - (11/24/2020)
### Fixed
+ Fixed auto refreshing of the access token when expired
+ testing: fixed testing for error messages on exceptions & testing of stale tokens

### Changed
+ Dependencies bump
    + certifi from 2020.6.20 to 2020.11.8
    + requests from 2.24.0 to 2.25.0
    + urllib3 from 1.25.10 to 1.26.2

### Added
+ Added Python 3.9 testing to CI


## [0.3.0] - (10/03/2020)
### Changed
+ Introduces multiple breaking changes compared to the previous version!
+ Dropped features related to the WorldCat Search API
+ Support for Worldcat Metadata API v.1.1 introduced in May 2020
+ Supported Metadata API endpoints:
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

### Added
+ API reference added to docs with mkapi

## 0.2.1 - (9/28/2020)
### Added
+ added functionality for docs versioning with mike

## 0.2.0 - (04/30/2020)
### Added
+ Expanded and improved documentation
+ Customizable "user-agent" in session header and token request
+ `TokenRequestError` exception added on failed access token request

### Changed
+ SRU/CQL query syntax aligned with OCLC specifications

### Fixed
+ fixed hooks info in docstrings in `SearchSession` and `MetadataSession`

[1.0.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.5...v0.4.0
[0.3.5]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v0.2.0...v0.3.0