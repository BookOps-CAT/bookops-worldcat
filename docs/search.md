# Search WorldCat
Bookops-Worldcat provides functionality that allows users to search WorldCat for brief bibliographic resources, holdings data, and classification recommendations. 

Requests made to any `/search/` endpoints return server responses in JSON format. These responses can be accessed and parsed with the `.json()` method.

## Brief Bib Resources
### Search Brief Bibs
The `brief_bibs_search` method allows users to query WorldCat using WorldCat's [bibliographic record indexes](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Bibliographic_records/Bibliographic_record_indexes).

The Metadata API many limiters that one can use to restrict query results. A full list of available parameters for the `brief_bibs_search` method is available in the [API Documentation](api/metadata_api.md#bookops_worldcat.metadata_api.MetadataSession.brief_bibs_search). Additional search examples are also available in the [Advanced Search Functionality](#advanced-search-functionality) section of this page.

Basic usage:
```python title="brief_bibs_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(
        q="ti: My brilliant friend AND au: Ferrante, Elena",
        inCatalogLanguage="eng",
        itemSubType="book-printbook",
        orderBy="mostWidelyHeld",
        )
    print(response.json())
```
```{ .json title="brief_bibs_search Response" .no-copy}
{
  "numberOfRecords": 79, 
  "briefRecords": [
    {
      "oclcNumber": "778419313", 
      "title": "My brilliant friend", 
      "creator": "Elena Ferrante", 
      "date": "2012", 
      "machineReadableDate": "2012", 
      "language": "eng", 
      "generalFormat": "Book", 
      "specificFormat": "PrintBook", 
      "publisher": "Europa Editions", 
      "publicationPlace": "New York, New York", 
      "isbns": [
        "9781609450786", 
        "1609450787"
      ], 
      "mergedOclcNumbers": [
        "811639683", 
        "818678733", 
        "824701856", 
        "829903719", 
        "830036387", 
        "1302347443"
      ], 
      "catalogingInfo": {
        "catalogingAgency": "BTCTA", 
        "catalogingLanguage": "eng", 
        "levelOfCataloging": " ", 
        "transcribingAgency": "BTCTA"
      }
    },
  ]
}
```

### Get Brief Bibs
Users can retrieve a brief bib resource for a known item by passing the OCLC Number for the resource to the `brief_bibs_get` method.

Basic usage:
```python title="brief_bibs_get Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_get(778419313)
    print(response.json())
```
```{ .json title="brief_bibs_get Response" .no-copy}
{
  "oclcNumber": "778419313",
  "title": "My brilliant friend",
  "creator": "Elena Ferrante",
  "date": "2012",
  "machineReadableDate": "2012",
  "language": "eng",
  "generalFormat": "Book",
  "specificFormat": "PrintBook",
  "publisher": "Europa Editions",
  "publicationPlace": "New York, New York",
  "isbns": [
    "9781609450786",
    "1609450787"
  ],
  "mergedOclcNumbers": [
    "811639683",
    "818678733",
    "824701856",
    "829903719",
    "830036387",
    "1302347443"
  ],
  "catalogingInfo": {
    "catalogingAgency": "BTCTA",
    "catalogingLanguage": "eng",
    "levelOfCataloging": " ",
    "transcribingAgency": "BTCTA"
  }
}
```
### Get Brief Bibs for Other Editions
Users can retrieve brief bib resources for other editions of a title by passing an OCLC Number to the `brief_bibs_get_other_editions` method.

Basic usage:
```python title="brief_bibs_get_other_editions Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_get_other_editions(
        oclcNumber="321339", 
        itemSubType="book-digital", 
        inCatalogLanguage="eng", 
        orderBy="bestMatch"
    )
    print(response.json())
```
```{ .json title="brief_bibs_get_other_editions Response" .no-copy}
{
  "numberOfRecords": 15, 
  "briefRecords": [
    {
      "oclcNumber": "859323121", 
      "title": "My brilliant friend. book one : childhood, adolescence", 
      "creator": "Elena Ferrante", 
      "date": "2012", 
      "machineReadableDate": "2012", 
      "language": "eng", 
      "generalFormat": "Book", 
      "specificFormat": "Digital", 
      "publisher": "Europa Editions", 
      "publicationPlace": "New York", 
      "isbns": [
        "9781609458638", 
        "160945863X", 
        "9781787701151", 
        "1787701158"
      ], 
      "mergedOclcNumbers": [
        "883320518", 
        "907236505", 
        "1030261956", 
        "1031563997", 
        "1032076035", 
        "1052184907", 
        "1124391373", 
        "1155208541", 
        "1191036210", 
        "1196835133"
      ], 
      "catalogingInfo": {
        "catalogingAgency": "TEFOD", 
        "catalogingLanguage": "eng", 
        "levelOfCataloging": " ", 
        "transcribingAgency": "TEFOD"
      }
    }, 
  ]
}
```
## Member Holdings
Users can query WorldCat for holdings data and return holdings summaries using Bookops-Worldcat and the Metadata API. Requests made using the `summary_holdings_search` and `shared_print_holdings_search` methods return brief bib resources with the holdings summaries in their responses, while requests made using the `summary_holdings_get` method only return holdings summaries. 

### Get Holdings Summary
Users can retrieve a summary of holdings data from WorldCat for a known item by passing an OCLC Number to the `summary_holdings_get` method. 

Basic Usage:
```python title="Basic summary_holdings_get Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_get("778419313")
    print(response.json())
```
```{ .json title="Basic summary_holdings_get Response" .no-copy}
{
  "totalHoldingCount": 1626,
  "totalSharedPrintCount": 5,
  "totalEditions": 1
}
```
Users can limit their search results to specific institutions, library types, or geographic areas.

Limit holdings search by state:
```python title="summary_holdings_get Request with heldInState limiter"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.summary_holdings_get("778419313", heldInState="US-NY")
  print(response.json())
```
```{ .json title="summary_holdings_get Response with heldInState limiter" .no-copy}
{
  "totalHoldingCount": 56,
  "totalSharedPrintCount": 0
}
```
### Search General Holdings
Users can pass either an OCLC Number, ISBN, or ISSN to the `summary_holdings_search` method to search for bibliographic resources their holdings.

Basic Usage:
```python title="summary_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_search(
        isbn="9781609458638", 
        heldInCountry="US"
    )
    print(response.json())
```
```{ .json title="summary_holdings_search Response" .no-copy}
{
  "numberOfRecords": 1, 
  "briefRecords": [
    {
      "oclcNumber": "859323121", 
      "title": "My brilliant friend. book one : childhood, adolescence", 
      "creator": "Elena Ferrante", 
      "date": "2012", 
      "machineReadableDate": "2012", 
      "language": "eng", 
      "generalFormat": "Book", 
      "specificFormat": "Digital", 
      "publisher": "Europa Editions", 
      "publicationPlace": "New York", 
      "isbns": [
        "9781609458638", 
        "160945863X", 
        "9781787701151", 
        "1787701158"
      ], 
      "mergedOclcNumbers": [
        "883320518", 
        "907236505", 
        "1030261956", 
        "1031563997", 
        "1032076035", 
        "1052184907", 
        "1124391373", 
        "1155208541", 
        "1191036210", 
        "1196835133"
      ], 
      "catalogingInfo": {
        "catalogingAgency": "TEFOD", 
        "catalogingLanguage": "eng", 
        "levelOfCataloging": " ", 
        "transcribingAgency": "TEFOD"
      }, 
      "institutionHolding": {
        "totalHoldingCount": 159
      }
    }
  ]
}
```
### Search Shared Print Holdings
To search just for holdings with retention commitments, users can pass an OCLC Number, ISBN, or ISSN to the `shared_print_holdings_search` method. The response includes the brief bib resource, a summary of shared print holdings for that resource, and data about the institutions with retention commitments for the resource.  

```python title="shared_print_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.shared_print_holdings_search(321339)
  print(response.json())
```
```{ .json title="shared_print_holdings_search Response" .no-copy}
{
  "numberOfRecords": 1, 
  "briefRecords": [
    {
      "oclcNumber": "778419313", 
      "title": "My brilliant friend", 
      "creator": "Elena Ferrante", 
      "date": "2012", 
      "machineReadableDate": "2012", 
      "language": "eng", 
      "generalFormat": "Book", 
      "specificFormat": "PrintBook", 
      "publisher": "Europa Editions", 
      "publicationPlace": "New York, New York", 
      "isbns": [
        "9781609450786", 
        "1609450787"
      ], 
      "mergedOclcNumbers": [
        "811639683", 
        "818678733", 
        "824701856", 
        "829903719", 
        "830036387", 
        "1302347443"
      ], 
      "catalogingInfo": {
        "catalogingAgency": "BTCTA", 
        "catalogingLanguage": "eng", 
        "levelOfCataloging": " ", 
        "transcribingAgency": "BTCTA"
      }, 
      "institutionHolding": {
        "totalHoldingCount": 5, 
        "briefHoldings": [
          {
            "country": "US", 
            "state": "US-ME", 
            "oclcSymbol": "CBY", 
            "registryId": 1233, 
            "institutionNumber": 90, 
            "institutionName": "Colby College", 
            "alsoCalled": "Miller Library", 
            "hasOPACLink": True, 
            "self": "https://worldcat.org/oclc-config/institution/data/1233", 
            "address": {
              "street1": "Miller Library", 
              "street2": "5124 Mayflower Hill", 
              "city": "Waterville",
              "state": "US-ME",
              "postalCode": "04901-8851", 
              "country": "US", 
              "lat": 44.564102, 
              "lon": -69.66333
            }, 
            "institutionType": "ACADEMIC"
          }
        ]
      }
    }
  ]
}
```
## Classification Recommendations
Version 2.0 of the Metadata API added a new endpoint that users can query to retrieve classification recommendations for known items. With Bookops-Worldcat, users can pass an OCLC Number to the `bib_get_classification` method and the response will contain the most popular classification for that item in both Dewey and LC. 

```python title="bib_get_classification Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.bib_get_classification("778419313")
  print(response.json())
```
```{ .json title="bib_get_classification Response" .no-copy}
{
  "dewey": {
    "mostPopular": [
      "853/.92"
    ]
  },
  "lc": {
    "mostPopular": [
      "PQ4866.E6345 A8113 2012"
    ]
  }
}
```
## Advanced Search Functionality

!!! info
    While most arguments passed to `/search/` endpoints (such as `brief_bibs_search`, `local_bibs_search`, and `summary_holdings_search`) are joined using the 'AND' operator, when both `itemType` and `itemSubType` are used in a query, they are joined using the 'OR' operator. 

### Keyword and Fielded Queries
The Metadata API provides robust search functionality for bib resources. In addition to a flexible query string that supports keyword and fielded searches, it is possible to set further limits using various elements such as item type, language, and publishing date. Users can specify the order of returned records by using the `orderBy` argument. 

The query syntax is case-insensitive and allows keyword and phrase search (use quotation marks around phrases), boolean operators (AND, OR, NOT), wildcards (# - single character, ? - any number of additional characters), and truncation (use \* character).

#### Advanced Search for Brief Bib Resources

More about the query syntax available for brief bib resource searches can be found in [OCLC's documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Bibliographic_records/Bibliographic_record_indexes/Bibliographic_record_index_lists).

Two equivalent `brief_bibs_search` examples with item type and language limiters:

=== "Keyword Search"

    ```python
      response = session.brief_bibs_search(
          q="ti=my brilliant friend",
            itemType="video",
            inLanguage="eng",
            orderBy="bestMatch",
          )
      print(response.json())
    ```
=== "Fielded Search"

    ```python
      response = session.brief_bibs_search(
          q='ti="my brilliant friend" AND x0: video AND ln: eng',
          orderBy="bestMatch"
          )
      print(response.json())
    ```

```{ .json  .no-copy}
{
  "numberOfRecords": 37, 
  "briefRecords": [
    {
      "oclcNumber": "1091307669", 
      "title": "My Brilliant Friend",
      "date": "2019", 
      "machineReadableDate": "2019", 
      "language": "eng", 
      "generalFormat": "Video", 
      "specificFormat": "DVD", 
      "edition": "Widescreen ed", 
      "publisher": "Home Box Office", 
      "publicationPlace": "[United States]", 
      "catalogingInfo": {
        "catalogingAgency": "CNWPU", 
        "catalogingLanguage": "eng", 
        "levelOfCataloging": "M", 
        "transcribingAgency": "CNWPU"
      }
    },
  ]
}
```

#### Advanced Search for Local Bib Resources 

The `local_bibs_search` method also allows for fielded queries. The available indexes are slightly different from those available for brief bib resource searches. For more information about the query syntax for local bib resources see [OCLC's documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Local_bibliographic_data_records/Local_bibliographic_data_record_indexes_A-Z).

`local_bibs_search` with language and date created as MARC limiters:
```python title="local_bibs_search Fielded Query"
session.local_bibs_search(q="ti=My Local Bib Record AND dc=2024? AND ln=eng")
```
