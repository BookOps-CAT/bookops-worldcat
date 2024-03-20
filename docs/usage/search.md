# Search WorldCat
Bookops-Worldcat provides functionality that allows users to search WorldCat for bibliographic resources, holdings data, and classification recommendations. 

## Brief Bib Resources
Server responses are returned in JSON format for requests made to any `/search/brief_bibs/` endpoints. These responses can be accessed and parsed with the `.json()` method.

### Search
The `brief_bibs_search` method allows users to query WorldCat using WorldCat's bibliographic record indexes.

Server responses are returned in JSON format by default for `brief_bibs_search` requests. This response can be accessed and parsed with the `.json()` method.

Basic usage:
```python title="brief_bibs_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(
        q="ti:The master and Margarita AND au: Bulgakov, Mikhail", 
        inLanguage="eng", 
        inCatalogLanguage="eng" 
        itemSubType="book-printbook", 
        orderBy="mostWidelyHeld"
    )
    print(response.json())
```
```json title="brief_bibs_search Response"
{
  "numberOfRecords": 190,
  "briefRecords": [
    {
      "oclcNumber": "321339",
      "title": "The master and Margarita",
      "creator": "Mikhail Bulgakov",
      "date": "©1967",
      "machineReadableDate": "1967",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "PrintBook",
      "edition": "1st U.S. ed",
      "publisher": "Harper & Row",
      "publicationPlace": "New York",
      "mergedOclcNumbers": [
        "68172169",
        "977269772",
        "992611164",
        "1053636208",
        "1086334687",
        "1089359174",
        "1126595016",
        "1154557860"
      ],
      "catalogingInfo": {
        "catalogingAgency": "DLC",
        "catalogingLanguage": "eng",
        "levelOfCataloging": "1",
        "transcribingAgency": "DLC"
      }
    }
  ]
}
```
The Metadata API has many indexes that can be used to facet one's searches. A full list of available parameters for the `brief_bibs_search` method is available in the [API Documentation](bookops_worldcat.metadata_api/#bookops_worldcatmetadata_apimetadatasessionbrief_bibs_search). Additional search examples are also available in the [Advanced Search Functionality](#advanced-search-functionality) section of this page.

### Retrieve Brief Bibs
Users can retrieve a brief bib resource for a known item by passing the OCLC Number for the resource to the `brief_bibs_get` method.

Basic usage:
```python title="brief_bibs_get Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_get(778419313)
    print(response.json())
```
```json title="brief_bibs_get Response"
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
### Retrieve Brief Bibs for Other Editions
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
```json title="brief_bibs_get_other_editions Response"
{
  "numberOfRecords": 71,
  "briefRecords": [
    {
      "oclcNumber": "1231604898",
      "title": "The Master and Margarita",
      "creator": "Mikhail Bulgakov",
      "date": "2021",
      "machineReadableDate": "2021",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "Digital",
      "publisher": "Alma Books",
      "publicationPlace": "London",
      "isbns": [
        "1847493920",
        "9781847493927"
      ],
      "catalogingInfo": {
        "catalogingAgency": "EBLCP",
        "catalogingLanguage": "eng",
        "levelOfCataloging": "M",
        "transcribingAgency": "EBLCP"
      }
    },
  ]
}
```
## Member Holdings
Requests made using the `summary_holdings_get`, `summary_holdings_search`, and `shared_print_holdings_search` methods return holdings summaries in JSON format. Requests made using the `summary_holdings_search` and `shared_print_holdings_search` methods also return brief bib resources in their responses.

### Get Holdings Summary
Users can retrieve a summary of holdings data from WorldCat for a known item by passing an OCLC Number to the `summary_holdings_get` method. 

Basic Usage:
```python title="summary_holdings_get Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_get("778419313")
    print(response.json)
```
```json title="summary_holdings_get Response"
{
  "totalHoldingCount": 1626,
  "totalSharedPrintCount": 5,
  "totalEditions": 1
}
```
Users can limit their search results to specific institutions, library types, or geographic areas.

Limit holdings search by state:
```python title="summary_holdings_get Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.summary_holdings_get("778419313", heldInState="US-NY")
  print(response.json)
```
```json title="summary_holdings_get Response"
{
  "totalHoldingCount": 56,
  "totalSharedPrintCount": 0
}
```
### Search General Holdings
To search for bibliographic resources and return their holdings summary, users can pass either and OCLC Number, ISBN, or ISSN to the `summary_holdings_search` method. 

Basic Usage:
```python title="summary_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_search(
        isbn="9781847493927", 
        heldInCountry="US"
    )
    print(response.json)
```
```json title="summary_holdings_search Response"
{
  "numberOfRecords": 1,
  "briefRecords": [
    {
      "oclcNumber": "1231604898",
      "title": "The Master and Margarita",
      "creator": "Mikhail Bulgakov",
      "date": "2021",
      "machineReadableDate": "2021",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "Digital",
      "publisher": "Alma Books",
      "publicationPlace": "London",
      "isbns": [
        "1847493920",
        "9781847493927"
      ],
      "catalogingInfo": {
        "catalogingAgency": "EBLCP",
        "catalogingLanguage": "eng",
        "levelOfCataloging": "M",
        "transcribingAgency": "EBLCP"
      },
      "institutionHolding": {
        "totalHoldingCount": 8
      }
    }
  ]
}
```
### Search Shared Print Holdings
To search just for holdings with a commitment to retain, users can pass an OCLC Number, ISBN, or ISSN to the `shared_print_holdings_search` method. The response includes the brief bib resource, a summary of shared print holdings for that resource, and data about the institutions with retention commitments for the resource.  

```python title="shared_print_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.shared_print_holdings_search(321339)
  print(response.json)
```
```json title="shared_print_holdings_search Response"
{
  "numberOfRecords": 1,
  "briefRecords": [
    {
      "oclcNumber": "321339",
      "title": "The master and Margarita",
      "creator": "Mikhail Bulgakov",
      "date": "©1967",
      "machineReadableDate": "1967",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "PrintBook",
      "edition": "1st U.S. ed",
      "publisher": "Harper & Row",
      "publicationPlace": "New York",
      "mergedOclcNumbers": [
        "68172169",
        "977269772",
        "992611164",
        "1053636208",
        "1086334687",
        "1089359174",
        "1126595016",
        "1154557860"
      ],
      "catalogingInfo": {
        "catalogingAgency": "DLC",
        "catalogingLanguage": "eng",
        "levelOfCataloging": "1",
        "transcribingAgency": "DLC"
      },
      "institutionHolding": {
        "totalHoldingCount": 16,
        "briefHoldings": [
          {
            "country": "US",
            "state": "US-MI",
            "oclcSymbol": "EYM",
            "registryId": 5293,
            "institutionNumber": 553,
            "institutionName": "University of Michigan",
            "alsoCalled": "University of Michigan - Ann Arbor",
            "hasOPACLink": true,
            "self": "https://worldcat.org/oclc-config/institution/data/5293",
            "address": {
              "street1": "818 Hatcher Graduate Library",
              "street2": "913 S. University Avenue",
              "city": "Ann Arbor",
              "state": "US-MI",
              "postalCode": "48109-1190",
              "country": "US",
              "lat": 42.2763,
              "lon": -83.7382
            },
            "institutionType": "ACADEMIC"
          },
        ]
      }
    }
  ]
}
```
## Classification Recommendations
Version 2.0 of the Metadata API added a new endpoint that users can query to retrieve classification recommendations for known items. With Bookops-Worldcat, users can pass an OCLC Number to the `bib_get_classification` method and the response will contain the most popular classification for that item in both Dewey and LC. The response will be returned in JSON format.

```python title="bib_get_classification Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
  response = session.bib_get_classification("778419313")
  print(response.json)
```
```json title="bib_get_classification Response"
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

!!! note
    Most arguments passed to `/search/` endpoints are joined using the 'AND' operator. When both `itemType` and `itemSubType` are used in a query, they are joined using the 'OR' operator. 

### Keyword and Fielded Queries
The Metadata API provides robust search functionality for bib resources. In addition to a flexible query string that supports keyword and fielded searches, it is possible to set further limits using various elements such as item type, language, and publishing date. Users can specify the order of returned records by using the `orderBy` argument. 

The query syntax is case-insensitive and allows keyword and phrase search (use quotation marks around phrases), boolean operators (AND, OR, NOT), wildcards (# - single character, ? - any number of additional characters), and truncation (use \* character).

[Phrase search](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Search/Types_of_searches/10Phrase_search)
!!! Note
    Queries should use double quotes ( " ) rather than single quotes ( ' ) in order to search with phrases.

#### Advanced Search for Brief Bib Resources

More about the query syntax available for brief bib resource searches can be found in [OCLC's documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Bibliographic_records/Bibliographic_record_indexes/Bibliographic_record_index_lists).

`brief_bibs_search` with item type, language and publishing date limiters:

=== "Keyword Search"

    ```python
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.brief_bibs_search(
            q="ti=the master and margarita",
            itemType="book",
            inLanguage="eng",
            datePublished="20##"
            orderBy="publicationDateDesc"
        )
        print(response.json())
    ```
    ```json
    ```
=== "Fielded Search"

    ```python
    session.brief_bibs_search(q="ti=the master and margarita AND x0=book AND ln=eng AND yr:20##", orderBy="publicationDateDesc")
    ```

#### Advanced Search for Local Bib Resources 

The `local_bibs_search` method also allows for both keyword and fielded queries. The available indexes are slightly different from those available for brief bib resource searches. For more information about the query syntax for local bib resources see [OCLC's documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Local_bibliographic_data_records/Local_bibliographic_data_record_indexes_A-Z).


```python title="Advanced summary_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_search()
    print(response.json)
```

```json title="Advanced summary_holdings_search Response"
```

### Advanced Holdings Searches 

`summary_holdings_search` with library type, item type, lat, lon, distance and unit limiters:

!!! note
    Most arguments passed to `/search/` endpoints are joined using the 'AND' operator. When both `itemType` and `itemSubType` are used in a query, they are joined using the 'OR' operator. 

```python title="Advanced summary_holdings_search Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.summary_holdings_search()
    print(response.json)
```

```json title="Advanced summary_holdings_search Response"
```