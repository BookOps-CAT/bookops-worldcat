# Changelog

## [1.2.0] - (6/16/2025)
### Added
 - Added support for new new Metadata API functionality:
   - `MetadataSession.branch_holding_codes_get()` allows users to retrieve branch holding codes and shelving locations using the `/worldcat/manage/institution-config/branch-shelving-locations` endpoint
   - `MetadataSession.institution_identifiers_get()` allows users to retrieve retrieve the Registry ID and OCLC Symbols for one or more institutions using the `/worldcat/search/institution` endpoint
   - `MetadataSession.holdings_move()` allows users to move holdings and all associated LHR and LBD records from one bib record to another using the `/worldcat/manage/institution/holdings/move` endpoint
 - Added `verify_ids` function in `utils.py` to check OCLC Symbols and Registry IDs before passing values to API

### Changed
 - restructured `pyproject.toml` following the changes implemented with poetry 2.0. Several sections of the `pyproject.toml` file have been moved from the `tool.poetry` section to the `project` section. 
   - The `project` section now includes `name`, `version`, `description`, `authors`, `license`, `keywords`, `dynamic` (a list of sections with dynamic metadata), `dependencies`, `requires-python`, and `readme`.
     - dev dependencies are still in the `tool.poetry.group.dev.dependencies` section
   - The `tool.poetry` section now includes:, `package-mode`, `exclude`, `packages`, and `classifiers`
     - `classifiers` is defined as having dynamic metadata in the `project` section   
   - The `tool.poetry.urls` section is now the `project.urls` section and includes other urls previously included in the `tool.poetry` section (ie. `repository` and `homepage`).
 - updated dependencies:
   - `requests` (2.32.4)
   - `coverage` (7.9.1)
   - `pytest` (8.4.0)
   - `pytest-cov` (6.2.1)
   - made `types-requests` a required dependency
 - updated `tool.pytest.ini_options` section to include coverage options
 - updated `tool.coverage.run` to omit `tests` and `docs` paths from coverage report 

### Fixed
 - Tests in `webtests/test_api_spec.py` that were failing due to new endpoints that were added in June 2025. 

### Removed
 - Support for python 3.8
 - `pytest-mock` as a dev dependency as it was unused.

## [1.1.1] - (4/15/2025)
### Added
 - `types-requests` as an extra dependency for type-checking purposes. Previously `types-requests` was just a dev dependency since `bookops-worldcat` is fully typed. Adding `types-requests` as an extra dependency will allow users to have the `requests` stubs needed to work with any `requests` objects. Without this any returned `requests` objects are typed as `Any`. This will not change anything for most users but it gives people the option to install the stubs for `requests`
### Changed
 - Changed process for retrieving Open API yaml file from OCLC documentation so that multiple requests are not sent
 - Changed fixtures that were only used to test API spec from `webtests/conftest.py` to `TestAPISpec` class
   - `method_params` is now `TestAPISpec.params_from_method`
   - `endpoint_params` is now `TestAPISpec.params_from_yaml`
   - `metadata_session_open_api_spec` is now `api_spec_dict` property
 - Changed tests in `webtests/test_metadata_api_live.py` to use `live_token` fixture rather than requesting a new token for each test
 - github actions now use `pipx` and `poetry` to install dependencies rather than `pip`
 - separated `dev` and `docs` dependencies within pyproject.toml  
 - Updated dependencies for docs:
 - `jinja2` (3.1.6)
### Fixed
 - Live tests that were failing or making multiple api requests:
   - Fixed error due to new, unannounced endpoint 
   - Added automatic retries to monthly automated live tests

## [1.1.0] - (11/15/2024)
### Added
+ Support for new Metadata API functionality:
  + `bib_search` method within `MetadataSession` class allows users to retrieve full MARC records in JSON format with the new `/worldcat/search/bibs/{oclcNumber}`
  + `cascadeDelete` arg added to `holdings_unset` and `holdings_unset_with_bib` methods. LHR and LBD records will be deleted when unsetting holdings on a record in WorldCat. This default functionality can be changed by setting `cascadeDelete` to `False`
+ Monthly live tests running via GitHub Actions
  + Tests will check whether changes have been made to the Metadata API
+ Python 3.13 added to unit tests
+ Type annotations added to fixtures in `conftest.py`
+ `scope` added as a return value in `WorldcatAccessToken` tests and documentation
  + OCLC's Authorization Server now accepts and returns `scope` as a parameter but it appears to be interchangeable with `scopes`. It is listed in the tests and documentation for `WorldcatAccessToken` but is not included as an attribute for the class.
+ Dev dependencies:
  + `types-pyyaml` (6.0.12)
### Changed
+ Moved live tests to separate files within `tests/webtests` directory
+ Moved fixtures for live tests to `tests/webtests/conftest.py`
+ Minor edits to tests due to changes in responses from Metadata API
+ Updated dependencies:
  + `certifi` (2024.8.30)
  + `charset-normalizer` (3.4.0)
  + `idna` (3.10)
  + `requests` (2.32.3)
  + `urllib3` (2.2.3)
+ Updated dev dependencies:
  + `babel` (2.16.0)
  + `black` (24.8.0)
  + `coverage` (7.6.1)
  + `exceptiongroup` (1.2.2)
  + `griffe` (1.4.0)
  + `importlib-metadata` (8.5.0)
  + `importlib-resources` (6.4.5)
  + `jinja2` (3.1.4)
  + `markdown` (3.7)
  + `mike` (2.1.3)
  + `mkdocs-autorefs` (1.2.0)
  + `mkdocs-get-deps` (0.2.0)
  + `mkdocs-material` (9.5.46)
  + `mkdocs` (1.6.1)
  + `mkdocstrings-python` (1.11.1)
  + `mkdocstrings` (0.26.1)
  + `mypy` (1.13.0)
  + `packaging` (24.2)
  + `paginate` (0.5.7)
  + `platformdirs` (4.3.6)
  + `pluggy` (1.5.0)
  + `pygments` (2.18.0)
  + `pymdown-extensions` (10.12)
  + `pyparsing` (3.1.4)
  + `pytest-mock` (3.14.0)
  + `python-dateutil` (2.9.0.post0)
  + `pytz` (2024.2)
  + `pyyaml` (6.0.2)
  + `regex` (2024.11.6)
  + `tomli` (2.1.0)
  + `types-requests` (2.32.0.20241016)
  + `typing-extensions` (4.12.2)
  + `urllib3` (2.2.3)
  + `watchdog` (4.0.2)
  + `wheel` (0.45.1)
  + `zipp` (3.20.2)
### Fixed
+ Return type for all `MetadataSession` methods is now `requests.Response` not `Optional[requests.Response]`
+ Typos and incorrect import statements
### Removed
+ Redundant/unused fixtures for mock 400 and 409 responses from `conftest.py`
+ Changed `stub_marc21` fixture to return `bytes` and removed `test.mrc` file

## [1.0.1] - (5/1/2024)
### Fixed
+ Inconsistent default values for `timeout` arg for `MetadataSession`, `WorldcatAccessToken` and `Query` objects
### Changed
+ Updated dev dependencies:
  + black (24.3.0)
+ Updated dependencies:
  + idna (3.7)
+ Reformatted docstrings for better readability on https://bookops-cat.github.io/bookops-worldcat/
+ Fixed typos
+ `prep_oclc_number_str` now parses OCLC Numbers with "(OCoLC)" prefix. Parsing rules match [OCLC documentation](https://help.oclc.org/Metadata_Services/WorldShare_Collection_Manager/Data_sync_collections/Prepare_your_data/30035_field_and_OCLC_control_numbers)
### Added
+ Tutorials to `tutorials.md`

## [1.0.0] - (3/22/2024)
### Added
+ Support for OCLC Metadata API Version 2.0
    + `MetadataSession` methods to support new functionality released in Metadata API 2.0
        + `bib_match`
        + `bib_get_classification`
        + `holdings_set_with_bib` and `holdings_unset_with_bib`
    + New `MetadataSession` methods to support existing Metadata API functionality
        + Bib Record Management and Validation
            + `bib_create`
            + `bib_replace`
            + `bib_validate`
        + Local Holdings Records
            + `lhr_create`
            + `lhr_delete`
            + `lhr_get`
            + `lhr_replace`
        + Local Bibliographic Data
            + `lbd_create`
            + `lbd_delete`
            + `lbd_get`
            + `lbd_replace`
        + Holdings Management
            + `holdings_get_codes`
+ Support for [automatic retries of failed requests](https://bookops-cat.github.io/bookops-worldcat/advanced/#token-refresh-and-request-retries)
+ Support for [multi-institution WSKeys](https://bookops-cat.github.io/bookops-worldcat/advanced/#identifying-your-institution)
+ Support for Python 3.11 and 3.12
+ New dev dependencies:
    + types-requests (2.31.0.20240125)
    + mkdocs-material (9.5.13)

### Changed
+ `MetadataSession` methods that have been renamed and updated (replacing existing functionality in Bookops-Worldcat): 
    + `get_brief_bib` is now `brief_bibs_get`
    + `get_full_bib` is now `bib_get`
    + `holding_get_status` is now `holdings_get_current`
    + `holding_set` is now `holdings_set`
    + `holding_unset` is now `holdings_unset`
    + `search_brief_bib_other_editions` is now `brief_bibs_get_other_editions`
    + `search_brief_bibs` is now `brief_bibs_search`
    + `search_current_control_numbers` is now `bib_get_current_oclc_number`
    + `search_general_holdings` is now `summary_holdings_search`
    + `search_shared_print_holdings` is now `shared_print_holdings_search` 
+ `WorldcatAccessToken` 
    + `scopes` arg now only accepts strings. A `TypeError` is raised if `scopes` arg is passed a list
    + `token_expires_at` attribute is now an aware `datetime` object (change made due to [`datetime.utcnow()`](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow) deprecation)
+ Error handling:
    + `TypeError` and `ValueError` replace `WorldcatAuthorizationError` when `WorldcatAccessToken` is passed an invalid arg.
    + `MetadataSession` now raises `InvalidOclcNumber` exception when invalid OCLC identifiers are given
+ `pytest` configuration moved from `pytest.ini` to `pyproject.toml`
+ Updated and clarified type annotations for `MetadataSession` methods
+ Updated dependencies:
    + requests: (2.31)
+ Updated dev dependencies:
    + black (23.3.0)
    + mike (2.0.0)
    + mypy (1.0.14)
+ Documentation on [https://bookops-cat.github.io/bookops-worldcat/](https://bookops-cat.github.io/bookops-worldcat/) has been rewritten and reorganized

### Fixed
+ `AttributeError` changed to `TypeError` if arg passed to `Query.prepared_request` is not a `PreparedRequest`
+ All args for methods within `MetadataSession` have been changed to camel case to be consisted with Metadata API documentation


### Removed
+ `principalID` and `principalIDNS` as args for `WorldcatAccessToken`
+ Automatic handling of large sets of oclcNumbers
    + `_split_into_legal_volume` removed from `MetadataSession`; a `ValueError` is now raised if a method is passed too many oclcNumbers


### Deprecated
+ Support for Python 3.7
+ 409 error handling for holdings set/unset requests 
+ `WorldcatSessionError` 
    + Replaced with `TypeError` or `ValueError` in `WorldcatSession`

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

[1.2.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/BookOps-CAT/bookops-worldcat/compare/v1.0.0...v1.0.1
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