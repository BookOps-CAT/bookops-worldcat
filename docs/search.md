The Metadata API allows users to search for bibliographic resources and holdings data in WorldCat.

After opening a `MetadataSession` is authenticated using the `WorldcatAccessToken` object, users can send requests to the Metadata API using the same parameters and configuration for each request.

## Brief Bib Resources
### Search
The `brief_bibs_search` method allows users to query WorldCat using WorldCat's bibliographic record indexes.

Server responses are returned in JSON format by default for `brief_bibs_search` requests. This response can be accessed with the `.json()` method.

Basic usage:
```python 
with MetadataSession(authorization=token) as session:
    response = session.brief_bibs_search(q="")
    print(response.json())
```
```json
```
### Retrieve Brief Bibs
Users can retrieve a brief bib resource for an OCLC Number using the `brief_bibs_get` method and can limit the results by providing additional parameters as part of the request.

Basic usage:
```python
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    results = session.brief_bibs_get(321339)
    print(results.json())
```
```json
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
```
### Retrieve Brief Bibs for Other Editions
Users can also retrieve brief bib resources for other editions of a title by passing an OCLC Number to the `brief_bibs_get_other_editions` method.

Basic usage:
```python
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    results = session.brief_bibs_get_other_editions(321339, itemSubType="book-digital")
    print(results.json())
```
```json
{
  "numberOfRecords": 71,
  "briefRecords": [
    {
      "oclcNumber": "951807890",
      "title": "The master and Margarita",
      "creator": "Mikhail Bulgakov",
      "date": "1997",
      "machineReadableDate": "1997",
      "language": "eng",
      "generalFormat": "Book",
      "specificFormat": "Digital",
      "publisher": "Penguin Books",
      "publicationPlace": "New York",
      "isbns": [
        "1524704121",
        "9781524704124"
      ],
      "catalogingInfo": {
        "catalogingAgency": "IDEBK",
        "catalogingLanguage": "eng",
        "levelOfCataloging": "M",
        "transcribingAgency": "IDEBK"
      }
    },
    ]
}
```

## Classification Recommendations
Users can get classification recommendations from the Metadata API by passing an OCLC Number to the `bib_get_classification` method. The output will contain the most popular classification in both Dewey and LC. 

```python
result = session.bib_get_classification("778419313")
print(result.json)
```
```json
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
## Member Holdings

### Get Holdings Summary
```python
result = session.summary_holdings_get()
print(result.json)
```
```json

```
### Search General Holdings
```python
result = session.summary_holdings_search()
print(result.json)
```

### Search Shared Print Holdings
```json

```

```python
result = session.shared_print_holdings_search()
print(result.json)
```
```json

```

## Advanced Search Functionality
### Keyword and Fielded Queries
The Metadata API provides quite robust methods to query WorldCat bibliographic resources and holdings data. In addition to a flexible query string that supports keyword and fielded searches, it is possible to set further limits using various elements such as type of item, language, and publishing date. Users can specify the order of returned records by using the `orderBy` argument. 

The query syntax is case-insensitive and allows keyword and phrase search (use quotation marks around phrases), boolean operators (AND, OR, NOT), wildcards (# - single character, ? - any number of additional characters), and truncation (use \* character).

More about the query syntax can be found in [OCLC's documentation](https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes/Get_started/Searching_WorldCat_indexes_guidelines_and_requirements).

!!! note
    Most arguments passed to `/search/` endpoints are joined using the 'AND' operator. When both `itemType` and `itemSubType` are used in a query, they are joined using the 'OR' operator. 

Search with item type, language and publishing date limiters:

=== "Keyword Search"

    ```py
    session.brief_bibs_search(
        q="czarne oceany dukaj",
        itemType="book",
        inLanguage="pol",
        datePublished="2015-2020"
        orderBy="publicationDateDesc"
    )
    ```

=== "Fielded Search"

    ```py
    session.brief_bibs_search(q="ti:'czarne oceany' AND au: 'dukaj' AND x0:'book' AND ln:'pol' AND yr:2015-2020", orderBy="publicationDateDesc")
    ```
