# Search and Manage Local Data
New functionality available in Version 1.0 of Bookops-Worldcat allows users to search and manage local bibliographic and holdings data via the Metadata API. 


### Manage Local Bib Records
Users can manage local bib records in WorldCat in the same way that they manage WorldCat records (see [Managing Bibliographic Records](manage_bibs.md) for more information). Records can be retrieved in MARCXML or MARC21 formats. The default format for records is MARCXML.  

=== "lbd_create"

    ```python title="lbd_create MARCXML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lbd_create(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)
    ```
    ```{ .xml title="lbd_create MARCXML Response" .no-copy}
    <record>
        <leader>00000n   a2200000   4500</leader>
        <controlfield tag="001">12345</controlfield>
        <controlfield tag="004">3160</controlfield>
        <controlfield tag="005">20240320120824.8</controlfield>
        <datafield tag="935" ind1=" " ind2=" ">
            <subfield code="a">MyLSN</subfield>
        </datafield>
        <datafield tag="940" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
        </datafield>
    </record>
    ```
=== "lbd_get"

    ```python title="lbd_get MARCXML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lbd_get("12345")
        print(response.content)

    ```
    ```{ .xml title="lbd_get MARCXML Response" .no-copy}
    <record>
        <leader>00000n   a2200000   4500</leader>
        <controlfield tag="001">12345</controlfield>
        <controlfield tag="004">3160</controlfield>
        <controlfield tag="005">20240320120824.8</controlfield>
        <datafield tag="935" ind1=" " ind2=" ">
            <subfield code="a">MyLSN</subfield>
        </datafield>
        <datafield tag="940" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
        </datafield>
    </record>
    ```

=== "lbd_replace"

    ```python title="lbd_replace MARCXML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lbd_replace(
                controlNumber="12345",
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)

    ```
    ```{ .xml title="lbd_replace MARCXML Response" .no-copy}
    <record>
        <leader>00000n   a2200000   4500</leader>
        <controlfield tag="001">12345</controlfield>
        <controlfield tag="004">3160</controlfield>
        <controlfield tag="005">20240320120824.8</controlfield>
        <datafield tag="935" ind1=" " ind2=" ">
            <subfield code="a">MyLSN</subfield>
        </datafield>
        <datafield tag="940" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
        </datafield>
    </record>
    ```

=== "lbd_delete"

    ```python title="lbd_delete MARCXML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lbd_delete("12345")
        print(response.content)

    ```
    ```{ .xml title="lbd_delete MARCXML Response" .no-copy}
    <record>
        <leader>00000n   a2200000   4500</leader>
        <controlfield tag="001">12345</controlfield>
        <controlfield tag="004">3160</controlfield>
        <controlfield tag="005">20240320120824.8</controlfield>
        <datafield tag="935" ind1=" " ind2=" ">
            <subfield code="a">MyLSN</subfield>
        </datafield>
        <datafield tag="940" ind1=" " ind2=" ">
            <subfield code="a">NYP</subfield>
        </datafield>
    </record>
    ```

## Search Local Bib Resources
Users can search for and retrieve brief local bib resources `local_bibs_get` and `local_bibs_search` methods. The response will be in JSON format.

=== "local_bibs_get"

    ```python title="local_bibs_get Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_bibs_get(123456789)
        print(response.json())
    ```
    ```{ .json title="local_bibs_get Response" .no-copy}
    {
      "controlNumber": 123456789,
      "oclcNumber": "987654321",
      "title": {
        "uniformTitles": [
          "Test Book"
          ]
        },
      "contributor": {
        "creators": [
          {
            "firstName": {
              "text": "Test"
            },
            "secondName": {
              "text": "Author"
            },
            "type": "person"
          }
        ]
      },
      "localSystemNumber": "System.Supplied@2024-03-20,11:50:40",
      "lastUpdated": 20240320
    }
    ```
=== "local_bibs_search"

    ```python title="local_bibs_search Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_bibs_search(q="ti: Test Book AND au: Test Author")
        print(response.json())
    ```
    ```{ .json title="local_bibs_search Response" .no-copy}
    {
      "numberOfRecords": 1,
      "records": [
        {
          "controlNumber": 123456789,
          "oclcNumber": "987654321",
          "title": {
            "uniformTitles": [
              "Test Book"
            ]
          },
          "contributor": {
          "creators": [
            {
              "firstName": {
                "text": "Test"
              },
              "secondName": {
                "text": "Author"
              },
              "type": "person"
            }
          ]
        },
        "localSystemNumber": "System.Supplied@2024-03-20,11:50:40",
        "lastUpdated": 20240320
        }
      ]
    }
    ```


## Manage Local Holdings Records
Users can manage local holdings records using Bookops-Worldcat in the same way that they manage local bib records (see above: [Managing Local Bib Records](#managing-local-bib-records) for more information).

=== "lhr_create"

    ```python title="lhr_create MARCXML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lhr_create(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)
    ```
    ```{ .xml title="lhr_create MARCXML Response" .no-copy}
    <record>
        <leader>00000nx  a2200000zi 4500</leader>
        <controlfield tag='004'>00001</controlfield>
        <controlfield tag='005'>20240320085741.4</controlfield>
        <controlfield tag='007'>zu</controlfield>
        <controlfield tag='008'>2403200p    0   4001uueng0210908</controlfield>
        <datafield ind2=' ' ind1=' ' tag='852'>
            <subfield code='a'>NYP</subfield>
            <subfield code='b'>TEST</subfield>
            <subfield code='c'>TEST-STACKS</subfield>
        </datafield>
        <datafield ind2=' ' ind1=' ' tag='876'>
            <subfield code='p'>00001</subfield>
        </datafield>
    </record>
    ```
=== "lhr_get"

    ```python title="lhr_get MARCXML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lhr_get("12345")
        print(response.content)

    ```
    ```{ .xml title="lhr_get MARCXML Response" .no-copy}
    <record>
        <leader>00000nx  a2200000zi 4500</leader>
        <controlfield tag='001'>12345</controlfield>
        <controlfield tag='004'>00001</controlfield>
        <controlfield tag='005'>20240320085741.4</controlfield>
        <controlfield tag='007'>zu</controlfield>
        <controlfield tag='008'>2403200p    0   4001uueng0210908</controlfield>
        <datafield ind2=' ' ind1=' ' tag='852'>
            <subfield code='a'>NYP</subfield>
            <subfield code='b'>TEST</subfield>
            <subfield code='c'>TEST-STACKS</subfield>
        </datafield>
        <datafield ind2=' ' ind1=' ' tag='876'>
            <subfield code='p'>00001</subfield>
        </datafield>
    </record>
    ```

=== "lhr_replace"

    ```python title="lhr_replace MARCXML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = io.BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lhr_replace(
                controlNumber="12345",
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)

    ```
    ```{ .xml title="lhr_replace MARCXML Response" .no-copy}
    <record>
        <leader>00000nx  a2200000zi 4500</leader>
        <controlfield tag='001'>12345</controlfield>
        <controlfield tag='004'>00001</controlfield>
        <controlfield tag='005'>20240320085741.4</controlfield>
        <controlfield tag='007'>zu</controlfield>
        <controlfield tag='008'>2403200p    0   4001uueng0210908</controlfield>
        <datafield ind2=' ' ind1=' ' tag='852'>
            <subfield code='a'>NYP</subfield>
            <subfield code='b'>TEST</subfield>
            <subfield code='c'>TEST-STACKS</subfield>
        </datafield>
        <datafield ind2=' ' ind1=' ' tag='876'>
            <subfield code='p'>00001</subfield>
        </datafield>
    </record>
    ```

=== "lhr_delete"

    ```python title="lhr_delete MARCXML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lhr_delete("12345")
        print(response.content)

    ```
    ```{ .xml title="lhr_delete MARCXML Response" .no-copy}
    <record>
        <leader>00000nx  a2200000zi 4500</leader>
        <controlfield tag='001'>12345</controlfield>
        <controlfield tag='004'>00001</controlfield>
        <controlfield tag='005'>20240320085741.4</controlfield>
        <controlfield tag='007'>zu</controlfield>
        <controlfield tag='008'>2403200p    0   4001uueng0210908</controlfield>
        <datafield ind2=' ' ind1=' ' tag='852'>
            <subfield code='a'>NYP</subfield>
            <subfield code='b'>TEST</subfield>
            <subfield code='c'>TEST-STACKS</subfield>
        </datafield>
        <datafield ind2=' ' ind1=' ' tag='876'>
            <subfield code='p'>00001</subfield>
        </datafield>
    </record>
    ```
### Managing Shared Print Commitments
Users can manage Shared Print collections using the Metadata API by adding Shared Print flags to their Local Holdings Records. More information on managing Shared Print commitments is available on [OCLC's Developer Network Site](https://www.oclc.org/developer/api/oclc-apis/worldcat-metadata-api/wcmetadata-faqs.en.html).

## Search Local Holdings Resources
Users can browse, search for and retrieve brief local holdings data in JSON format using the `local_holdings_get`, `local_holdings_search`, `local_holdings_browse`, and `local_holdings_search_shared_print` methods:

=== "local_holdings_get"

    ```python title="local_holdings_get Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_holdings_get(controlNumber="111111111")
        print(response.json())
    ```
    ```{ .json title="local_holdings_get Response" .no-copy}
    {
      "numberOfHoldings": 1,
      "detailedHoldings": [
        {
          "lhrControlNumber": "111111111",
          "lhrDateEntered": "20240101",
          "lhrLastUpdated": "20240201",
          "oclcNumber": "123456789",
          "format": "zu",
          "location": {
            "holdingLocation": "NYP",
            "sublocationCollection": "TEST",
            "shelvingLocation": "TEST-STACKS"
          },
          "copyNumber": "1",
          "callNumber": {
            "displayCallNumber": "TEST",
            "classificationPart": "TEST"
          },
          "hasSharedPrintCommitment": "N",
          "summary": "Local holdings available.",
          "holdingParts": [
            {
            "pieceDesignation": "TEST12345"
            }
          ]
        }
      ]
    }
    ```
=== "local_holdings_search"

    ```python title="local_holdings_search Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_holdings_search(
            oclcNumber="123456789", 
            orderBy="location"
            )
        print(response.json())
    ```
    ```{ .json title="local_holdings_search Response" .no-copy}
    {
      "numberOfHoldings": 1,
      "detailedHoldings": [
        {
          "lhrControlNumber": "111111111",
          "lhrDateEntered": "20240101",
          "lhrLastUpdated": "20240201",
          "oclcNumber": "123456789",
          "format": "zu",
          "location": {
            "holdingLocation": "NYP",
            "sublocationCollection": "TEST",
            "shelvingLocation": "TEST-STACKS"
          },
          "copyNumber": "1",
          "callNumber": {
            "displayCallNumber": "TEST",
            "classificationPart": "TEST"
          },
          "hasSharedPrintCommitment": "N",
          "summary": "Local holdings available.",
          "holdingParts": [
            {
            "pieceDesignation": "TEST12345"
            }
          ]
        }
      ]
    }
    ```
=== "local_holdings_browse"

    ```python title="local_holdings_browse Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_holdings_browse(
            callNumber="ReCAP-000000", 
            holdingLocation="TEST-LOCATION",
            shelvingLocation="TEST-STACKS",
            )
        print(response.json())
    ```
    ```{ .json title="local_holdings_browse Response" .no-copy}
    {
      "numberOfRecords": 1,
      "entries": [
        {
          "displayCallNumber": "ReCAP-000000",
          "holdingLocation": "TEST-LOCATION",
          "shelvingLocation": "TEST-STACKS",
          "pieceDesignation": "123456789",
          "oclcNumber": 000000000,
          "title": "Test",
          "creator": "Author, Test",
          "date": "2024",
          "language": "eng",
          "generalFormat": "Book",
          "specificFormat": "PrintBook",
          "edition": "1st ed.",
          "publisher": "Test",
          "publicationPlace": "New York :"
        },
      ]
    }
    ```

=== "local_holdings_search_shared_print"

    ```python title="local_holdings_search_shared_print Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.local_holdings_search_shared_print(
            oclcNumber="123456789", 
            orderBy="location"
            )
        print(response.json())
    ```
    ```{ .json title="local_holdings_search_shared_print Response" .no-copy}
    {
      "numberOfHoldings": 1,
      "detailedHoldings": [
        {
          "lhrControlNumber": "111111111",
          "lhrDateEntered": "20240101",
          "lhrLastUpdated": "20240201",
          "oclcNumber": "123456789",
          "format": "zu",
          "location": {
            "holdingLocation": "NYP",
            "sublocationCollection": "TEST",
            "shelvingLocation": "TEST-STACKS"
          },
          "copyNumber": "1",
          "callNumber": {
            "displayCallNumber": "TEST",
            "classificationPart": "TEST"
          },
          "hasSharedPrintCommitment": "Y",
          "summary": "Local holdings available.",
          "holdingParts": [
            {
            "pieceDesignation": "TEST12345"
            }
          ]
        }
      ]
    }
    ```