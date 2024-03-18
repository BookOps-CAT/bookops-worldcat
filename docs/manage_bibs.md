Users can manage bib records in WorldCat using a wide array of functionality.

## Get Full MARC Records
Calling the `bib_get` method with an OCLC number as an argument sends a request to retrieve the full bibliographic record in WorldCat. The Metadata API correctly matches requested OCLC numbers of records that have been merged together by returning the current master record. Records can be retrieved in MARC/XML or MARC 21 formats. The default format for retrieved records is MARC/XML.  

The response is a `requests.Response` object with all its features:
```python
with MetadataSession(authorization=token) as session:
    result = session.bib_get("321339")
    print(result.status_code)
    print(result.url)
200
"https://metadata.api.oclc.org/worldcat/manage/bibs/321339"
```
To avoid raising a `UnicodeEncodeError` when requesting full bib records it is recommended that one access the response data using the `.content` attribute of the response object:

```python
print(response.content)
```
## Get Current OCLC Numbers
The `bib_get_current_oclc_number` method allows users to retrieve the current control number of the master record in WorldCat. Occasionally, records identified as duplicates in WorldCat have been merged and in that case a local control number may not correctly refer to an OCLC master record. 

```python
with MetadataSession(authorization=token) as session:
    result = session.bib_get_current_oclc_number("992611164")
    print(result.status_code)
    print(result.url)
200
"https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=992611164"
```
```json
{
  "controlNumbers": [
    {
      "requested": "992611164",
      "current": "321339"
    }
  ]
}
```

## Match Bib Records

Users can pass a bib record in MARC/XML or MARC21 to the `bib_match` method. The web service will identify the best match for the record in WorldCat and return a brief bib resource in JSON.
```python
with open("file.xml","rb") as xml_file:
    for r in xml_file:
        xml_record = io.BytesIO(r)
        output = session.bib_match(record=xml_record, recordFormat="application/marcxml+xml")
        print(output.content)
```
```json
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
            "edition": "", 
            "publisher": "Europa Editions", 
            "publicationPlace": "New York, New York", 
            "isbns": ["9781609450786", "1609450787"], 
            "issns": [], 
            "mergedOclcNumbers": 
            ["811639683", "818678733", "824701856", "829903719", "830036387", "1302347443"], 
            "catalogingInfo": 
            {
                "catalogingAgency": "BTCTA", 
                "catalogingLanguage": "eng", 
                "levelOfCataloging": " ", 
                "transcribingAgency": "BTCTA"
                }
        }
    ]
}
```

## Advanced Bib Record Functionality
After opening a `MetadataSession` users with read-write access to the Metadata API can retrieve, replace, validate, and create WorldCat records.

### Create Bib Records
The `bib_create` method will create a new record in WorldCat when passed a valid MARC record in MARC/XML or MARC21 format. 

### Replace Bib Records
The `bib_replace` method will replace a WorldCat record with the record is it passed in the request body. 

### Validate Bib Records
Users can first pass their MARC records to the `bib_validate` method in order to avoid parsing errors when creating or updating WorldCat records. This will check the formatting and quality of the bib record and return either errors identified in the record or a brief JSON response confirming that the record is valid.

```
add example of bib_validate
```
When passing MARC records to any of the `/manage/bibs/` endpoints, users should ensure that data passed in the request body using the `record` argument matches the format of the `recordFormat` argument.
