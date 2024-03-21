# Manage Institution Holdings

Server responses are returned in JSON format for requests made to any `/manage/holdings/` endpoints. These responses can be accessed and parsed with the `.json()` method.

## Get Institution Holdings Codes

The `holdings_get_codes` method retrieves an institution's holdings codes. The web service identifies the institution based on the data passed to the `WorldcatAccessToken`.

```python title="holdings_get_codes Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.holdings_get_codes()
    print(response.json())
```
```{ .json title="holdings_get_codes Response" .no-copy}
{
  "holdingLibraryCodes": [
    {
      "code": "Rodgers & Hammerstein",
      "name": "NYPH"
    },
    {
      "code": "Schomburg Center",
      "name": "NYP3"
    },
    ]
}
```

## Get Current Holdings
The `holdings_get_current` method retrieves the holding status of a requested record for the authenticated institution.

```python title="holdings_get_current Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.holdings_get_current(oclcNumbers=123456789)
    print(response.json())
```
```{ .json title="holdings_get_current Response" .no-copy}
{
  "holdings": [
    {
      "requestedControlNumber": "123456789",
      "currentControlNumber": "123456789",
      "institutionSymbol": "NYP",
      "holdingSet": true
    }
  ]
}
```
## Set and Unset Holdings
Users can set and/or unset holdings in WorldCat by passing an OCLC Number to the `holdings_set` and/or `holdings_unset` methods. 

!!! info
    In version 2.0 of the Metadata API, users are no longer able to set holdings on multiple records at the same time. Users should now pass one OCLC Number per request to `holdings_set` and `holdings_unset`.

Version 2.0 of the Metadata API provides new functionality to set and unset holdings in WorldCat by passing the Metadata API a MARC record in MARCXML or MARC21 format. The record must have an OCLC number in the 035 or 001 field in order to set holdings in WorldCat.

Bookops-Worldcat supports this functionality with the `holdings_set_with_bib` and `holdings_unset_with_bib` methods which can be passed a MARC record in the body of the request in the same way that one would pass a record to a method that uses any of the `/manage/bibs/` endpoints.

=== "holdings_set"

    ```python title="holdings_set Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.holdings_set(oclcNumber=123456789)
        print(response.json())
    ```
    ```{ .json  title="holdings_set Response" .no-copy}
    {
      "controlNumber": "123456789",
      "requestedControlNumber": "123456789",
      "institutionCode": "58122",
      "institutionSymbol": "NYP",
      "success": true,
      "message": "Holding Updated Successfully",
      "action": "Set Holdings"
    }
    ```

=== "holdings_unset"

    ```python  title="holdings_unset Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.holdings_unset(oclcNumber=123456789)
        print(response.json())
    ```
    ```{ .json title="holdings_unset Response" .no-copy}
    {
      "controlNumber": "123456789",
      "requestedControlNumber": "123456789",
      "institutionCode": "58122",
      "institutionSymbol": "NYP",
      "success": true,
      "message": "Holding Updated Successfully",
      "action": "Unset Holdings"
    }
    ```

=== "holdings_set_with_bib"

    ```python title="holdings_set_with_bib Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO
    
    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.holdings_set_with_bib(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.json())
    ```
    ```{ .json title="holdings_set_with_bib Response" .no-copy}
    {
      "controlNumber": "123456789",
      "requestedControlNumber": "123456789",
      "institutionCode": "58122",
      "institutionSymbol": "NYP",
      "success": true,
      "message": "Holding Updated Successfully",
      "action": "Set Holdings"
    }
    ```

=== "holdings_unset_with_bib"

    ```python title="holdings_unset_with_bib Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO
    
    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.holdings_unset_with_bib(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.json())
    ```
    ```{ .json title="holdings_unset_with_bib Response" .no-copy}
    {
      "controlNumber": "123456789",
      "requestedControlNumber": "123456789",
      "institutionCode": "58122",
      "institutionSymbol": "NYP",
      "success": true,
      "message": "Holding Updated Successfully",
      "action": "Unset Holdings"
    }
    ```