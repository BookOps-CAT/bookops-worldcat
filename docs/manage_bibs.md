# Manage Bibliographic Records

!!! note
    Users must have "WorldCatMetadataAPI:manage_bibs" in the list of scopes for their WSKeys in order to manage bib records using the Metadata API. To check if your WSKey has access to these endpoints, log into your [WSKey Management portal](https://platform.worldcat.org/wskey/). 

## Get Full MARC Records
Users can retrieve full MARC records from WorldCat by passing the `bib_get` method an OCLC number. The Metadata API correctly matches OCLC numbers of records that have been merged together and returns the current master record. Records can be retrieved in MARCXML or MARC21 formats. The default format is MARCXML.  

```python title="bib_get"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.bib_get("321339")
    print(response.status_code)
#>200
    print(response.url)
#>"https://metadata.api.oclc.org/worldcat/manage/bibs/321339"
```

To avoid raising a `UnicodeEncodeError` when requesting full bib records it is recommended that one access the response data using the `.content` attribute of the response object:

=== "MARCXML"

    ```python title="bib_get MARCXML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.bib_get("321339")
        print(response.content)

    ```
    ```{ .xml title="bib_get MARCXML Response" .no-copy}
    <?xml version='1.0' encoding='UTF-8'?>
      <record xmlns="http://www.loc.gov/MARC21/slim">
        <leader>00000cam a22000001a 4500</leader>
        <controlfield tag="001">ocm00321339</controlfield>
        <controlfield tag="003">OCoLC</controlfield>
        <controlfield tag="005">20240202180208.2</controlfield>
        <controlfield tag="008">711005s1967    nyu           000 f eng  </controlfield>
        <datafield tag="010" ind1=" " ind2=" ">
          <subfield code="a">   67022898 </subfield>
        </datafield>
    <!--...-->
        <datafield tag="100" ind1="1" ind2=" ">
          <subfield code="a">Bulgakov, Mikhail,</subfield>
          <subfield code="d">1891-1940.</subfield>
        </datafield>
        <datafield tag="240" ind1="1" ind2="0">
          <subfield code="a">Master i Margarita.</subfield>
          <subfield code="l">English</subfield>
        </datafield>
        <datafield tag="245" ind1="1" ind2="4">
          <subfield code="a">The master and Margarita /</subfield>
          <subfield code="c">Mikhail Bulgakov ; translated from the Russian by Michael Glenny.</subfield>
        </datafield>
    <!--...-->
    </record>
    ```

=== "MARC21"

    ```python title="bib_get MARC21 Request"
    from bookops_worldcat import MetadataSession
    
    with MetadataSession(authorization=token) as session:
        response = session.bib_get("321339", responseFormat="application/marc")
        print(response.content)
    ```
    ```{ .text title="bib_get MARC21 Response" .no-copy}
    04305cam a22007691a 4500001001200000003000600012005001700018008004100035010001700076040024300093016002500336019009500361029002200456029002100478029001800499029002200517035016600539037001700705041001300722043001200735050001900747050002500766055002600791082001700817100003500834240003300869245009800902250001701000260003901017300002701056336002601083337002801109338002701137500001101164500016401175500008201339500003201421520019801453546004501651505080201696583004802498651002702546650001602573650002402589651004702613651003002660651002302690651002502713655002302738655001602761655005802777655004802835655002102883655001802904655002802922655002302950655003002973655002303003655002903026655002203055655002503077700002103102700004003123758015803163776017003321938004403491\x1eocm00321339\x1eOCoLC\x1e20240202180208.2\x1e711005s1967    nyu           000 f eng  \x1faBulgakov, Mikhail,\x1fd1891-1940.\x1e10\x1faMaster i Margarita.\x1flEnglish\x1e14\x1faThe master and Margarita /\x1fcMikhail Bulgakov ; translated from the Russian by Michael Glenny.
    ```


## Get Current OCLC Numbers
The `bib_get_current_oclc_number` method allows users to retrieve the current control number of a WorldCat record. Occasionally, records identified as duplicates in WorldCat have been merged and in that case a local control number may not correctly refer to the WorldCat record. 

```python title="bib_get_current_oclc_number Request"
from bookops_worldcat import MetadataSession

with MetadataSession(authorization=token) as session:
    response = session.bib_get_current_oclc_number("992611164")
    print(response.json())
```
```{ .json title="bib_get_current_oclc_number Response" .no-copy}
{
  "controlNumbers": [
    {
      "requested": "992611164",
      "current": "321339"
    }
  ]
}
```
## Advanced Bib Record Functionality
Several of the `/manage/bibs/` endpoints take a MARC record in the body of the request. When passing MARC records to any of these endpoints, users should ensure that the format passed in the `recordFormat` argument matches the format of the data passed in the request body using the `record` argument.

### Match Bib Records

Users can pass a bib record in MARCXML or MARC21 to the `bib_match` method and the web service will identify the best match for the record in WorldCat. The response will be a brief bib resource in JSON.

=== "MARCXML"

    ```python title="bib_match Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_match(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.json())
    ```

=== "MARC21"

    ```python title="bib_match Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.mrc","rb") as mrc_file:
        for r in mrc_file:
            mrc_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_match(
                record=mrc_record, 
                recordFormat="application/marc"
            )
            print(response.json())
    ```

```{ .json title="bib_match Response" .no-copy}
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
      "isbns": [], 
      "issns": [], 
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


### Create Bib Records
Users can create new WorldCat records using the `bib_create` method. The web service will check if the record exists in WorldCat and create a new record if it does not. Users should pass passed a valid MARC record in MARCXML or MARC21 format in the body of the request. 

The response returned by the web service will contain the WorldCat record in the format specified in the `responseFormat` parameter with its newly added OCLC Number.

!!! note
    It is recommended that users validate their records before trying to create new records in WorldCat in order to avoid errors. See [`bib_validate`](#validate-bib-records) below.

=== "MARCXML"

    ```python title="bib_create Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_create(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(xml_record)
            print(response.content)
    ```
    ```{ .xml title="bib_create Test Record" .no-copy}
    <record>
        <leader>00000nam a2200000 a 4500</leader>
        <controlfield tag="008">240320s2024    nyua          000 0 eng d</controlfield>
        <datafield tag="010" ind1=" " ind2=" ">
            <subfield code="a">   12345678 </subfield>
        </datafield>
        <datafield tag="040" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
            <subfield code="b">eng</subfield>
            <subfield code="c">NYP</subfield>
        </datafield>
        <datafield tag="100" ind1="0" ind2=" ">
            <subfield code="a">BookOps</subfield>
        </datafield>
        <datafield tag="245" ind1="1" ind2="0">
            <subfield code="a">Test Record</subfield>
        </datafield>
        <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">BOOKOPS-WORLDCAT DOCUMENTATION</subfield>
        </datafield>
    </record>
    ```
    ```{ .xml title="bib_create Response" .no-copy}
    <record>
        <leader>00000nam a2200000 a 4500</leader>
        <controlfield tag="001">ocn123456789</controlfield>
        <controlfield tag="008">240320s2024    nyua          000 0 eng d</controlfield>
        <datafield tag="010" ind1=" " ind2=" ">
            <subfield code="a">   12345678 </subfield>
        </datafield>
        <datafield tag="040" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
            <subfield code="b">eng</subfield>
            <subfield code="c">NYP</subfield>
        </datafield>
        <datafield tag="100" ind1="0" ind2=" ">
            <subfield code="a">BookOps</subfield>
        </datafield>
        <datafield tag="245" ind1="1" ind2="0">
            <subfield code="a">Test Record</subfield>
        </datafield>
        <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">BOOKOPS-WORLDCAT DOCUMENTATION</subfield>
        </datafield>
    </record>
    ```

=== "MARC21"

    ```python title="bib_create Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.mrc","rb") as mrc_file:
        for r in mrc_file:
            mrc_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_create(
                record=mrc_record, 
                recordFormat="application/marc"
            )
            print(mrc_record)
            print(response.text)
    ```
    ```{ .text title="bib_create Test Record" .no-copy}
    00266nam a2200097 a 4500008004100000010001700041040002200058100002700080245001600107500004500123\u001E240320s2024    nyua          000 0 eng d\u001E  \u001Fa   63011276 \u001E  \u001FaNYP\u001Fbeng\u001FcNYP\u001E0 \u001FaBookOps\u001E10\u001FaTest Record\u001E  \u001FaBOOKOPS-WORLDCAT DOCUMENTATION\u001E\u001D    
    ```
    ```{ .text title="bib_create Response" .no-copy}
    00291nam a2200109 a 4500001001300000008004100013010001700054040002200071100002700093245001600120500004500136\u001Eocn123456789\u001E240320s2024    nyua          000 0 eng d\u001E  \u001Fa   63011276 \u001E  \u001FaNYP\u001Fbeng\u001FcNYP\u001E0 \u001FaBookOps\u001E10\u001FaTest Record\u001E  \u001FaBOOKOPS-WORLDCAT DOCUMENTATION\u001E\u001D 
    ```

### Replace Bib Records
The `bib_replace` method will retrieve a record in WorldCat and replace it with the record it is passed in the request body. If the record does not exist, a new WorldCat record will be created.

=== "MARCXML"

    ```python title="bib_replace Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_replace(
                oclcNumber="123456789"
                record=xml_record,
                recordFormat="application/marcxml+xml",
            )
    ```

=== "MARC21"

    ```python title="bib_replace Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.mrc","rb") as mrc_file:
        for r in mrc_file:
            mrc_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_replace(
                record=mrc_record, 
                recordFormat="application/marc"
            )
    ```

### Validate Bib Records
Users can first pass their MARC records to the `bib_validate` method in order to avoid parsing errors when creating or updating WorldCat records. This will check the formatting and quality of the bib record and return either errors identified in the record or a brief JSON response confirming that the record is valid.

=== "MARCXML"

    ```python title="bib_validate Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_validate(
                record=xml_record,
                recordFormat="application/marcxml+xml",
                validationLevel="validateFull",
            )
            print(response.json())
    ```
=== "MARC21"

    ```python title="bib_validate Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.mrc","rb") as mrc_file:
        for r in mrc_file:
            mrc_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.bib_validate(
                record=mrc_record,
                recordFormat="application/marc",
                validationLevel="validateFull",
            )
            print(response.json())
    ```

```{ .json title="bib_validate Response" .no-copy}
{
    "httpStatus": "OK",
    "status": {
        "summary": "VALID",
        "description": "The provided Bib is valid"
    }
}
```