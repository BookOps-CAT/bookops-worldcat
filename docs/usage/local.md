# Search and Manage Local Data
New functionality available in Version 1.0 of Bookops-Worldcat allows users to search and manage local bibliographic and holdings data via the Metadata API. 


### Managing Local Bib Records
Users can manage local bib records in WorldCat in the same way that they manage WorldCat records (see [Managing Bibliographic Records](/bookops-worldcat/usage/manage_bibs/) for more information). Records can be retrieved in MARC/XML or MARC 21 formats. The default format for records is MARC/XML.  

=== "lbd_create"

    ```python title="lbd_create MARC/XML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = io.BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lbd_create(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)
    ```
    ```xml title="lbd_create MARC/XML Response"
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

    ```python title="lbd_get MARC/XML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lbd_get("12345")
        print(response.content)

    ```
    ```xml title="lbd_get MARC/XML Response"
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

    ```python title="lbd_replace MARC/XML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = io.BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lbd_replace(
                controlNumber="12345",
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)

    ```
    ```xml title="lbd_replace MARC/XML Response"
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

    ```python title="lbd_delete MARC/XML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lbd_delete("12345")
        print(response.content)

    ```
    ```xml title="lbd_delete MARC/XML Response"
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

## Searching Local Bib Resources
`local_bibs_get`/`local_bib_data_get`
`local_bibs_search`/`local_bib_data_search`


## Managing Local Holdings Records
Users can manage local holdings records in WorldCat in the same way that they manage local bib records (see above: [Managing Local Bib Records](#managing-local-bib-records) for more information).

=== "lhr_create"

    ```python title="lhr_create MARC/XML Request"
    from bookops_worldcat import MetadataSession
    from io import BytesIO

    with open("file.xml","rb") as xml_file:
        for r in xml_file:
            xml_record = io.BytesIO(r)
            session = MetadataSession(authorization=token)
            response = session.lhr_create(
                record=xml_record, 
                recordFormat="application/marcxml+xml"
            )
            print(response.content)
    ```
    ```xml title="lhr_create MARC/XML Response"
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
=== "lhr_get"

    ```python title="lhr_get MARC/XML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lhr_get("12345")
        print(response.content)

    ```
    ```xml title="lhr_get MARC/XML Response"
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

=== "lhr_replace"

    ```python title="lhr_replace MARC/XML Request"
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
    ```xml title="lhr_replace MARC/XML Response"
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

=== "lhr_delete"

    ```python title="lhr_delete MARC/XML Request"
    from bookops_worldcat import MetadataSession

    with MetadataSession(authorization=token) as session:
        response = session.lhr_delete("12345")
        print(response.content)

    ```
    ```xml title="lhr_delete MARC/XML Response"
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

## Searching Local Holdings Resources
`local_holdings_search_shared_print`/`local_holdings_data_search_shared_print`
`local_holdings_get`/`local_holdings_data_get`
`local_holdings_search`/`local_holdings_data_search`
`local_holdings_browse`/`local_holdings_data_browse`
