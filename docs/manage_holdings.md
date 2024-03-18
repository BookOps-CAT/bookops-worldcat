Users can perform several holdings operations using the Metadata API and Bookops-Worldcat wrapper. 

## Get Institution Holdings Codes

The `holdings_get_codes` method retrieves an institution's holdings codes based on the authentication data passed to a `WorldcatAccessToken`.

```python title="Get Holdings Codes"
result = session.holdings_get_codes()
print(result.json())
```
```json title="Holdings Codes Server Response"
{
  "holdingLibraryCodes": [
    {
      "code": "Rodgers & Hammerstein",
      "name": "NYPH"
    },
    {
      "code": "Schomburg-Photographs",
      "name": "NYP2"
    },
    {
      "code": "Schomburg Center",
      "name": "NYP3"
    },
    ]
}
```

## Get Current Holdings
The `holdings_get_current` method retrieves the holding status of a requested record using the OCLC Number. 

Example:
```python title="Get Current Holdings"
result = session.holdings_get_current(oclcNumbers=778419313)
print(result.json())
```

```json title="Current Holdings"
{
  "holdings": [
    {
      "requestedControlNumber": "778419313",
      "currentControlNumber": "778419313",
      "institutionSymbol": "NYP",
      "holdingSet": true
    }
  ]
}
```
## Set and Unset Holdings
### With OCLC Numbers
Used in conjunction with `holdings_set` and/or `holdings_unset`, users can check whether their institution has holdings set on a particular record and then set or unset the holdings.

=== "Set Holdings"

    ```py
    result = session.holdings_set(oclcNumber=778419313)
    print(result.json()["action"])
    Set Holdings
    ```

=== "Unset Holdings"

    ```py
    result = session.holdings_unset(oclcNumber=778419313)
    print(result.json()["action"])
    Unset Holdings
    ```

In version 2.0 of the Metadata API, users are no longer able to set holdings on multiple records at the same time. Users should now pass one OCLC Number per request to `holdings_set` and `holdings_unset`.


### With MARC Records
Version 2.0 of the Metadata API provides new functionality to set and unset holdings in WorldCat by passing the Metadata API a MARC record in MARC/XML or MARC21 format. The record must have an OCLC number in the 035 or 001 field in order to set holdings in WorldCat.

Bookops-Worldcat supports this functionality with the `holdings_set_with_bib` and `holdings_unset_with_bib` methods which can be passed a MARC record in the body of the request in the same way that one would pass a record to a method that uses any of the `/manage/bibs/` endpoints.

```
example with holdings_set_with_bib
```
