# Tutorials
The following tutorials illustrate how bookops-worldcat can be used for specific use cases in technical services workflows. These examples use [pymarc](https://pymarc.readthedocs.io/en/latest/) and modules from the Python standard library in addition to bookops-worldcat. All modules or libraries used in an example are be listed as imports at the top of the code snippet. 

??? note "Tutorial helper functions" 
    This tutorial uses the following helper functions:

    === "get_token"

        ```python
        def get_token(filepath: str) -> WorldcatAccessToken:
            """
            Retrieves user's WSKey credentials from .json file.
            The format of the credentials in the .json file should be:
                {
                    "key": "my_key",
                    "secret": "my_secret",
                    "scopes": "WorldcatMetadataAPI",
                    "agent": "MyApp/1.0"
                } 

            Args:
                filepath: path to location of json file with credentials

            Returns:
                WorldcatAccessToken
            """
            with open(filepath, "r") as file:
                data = json.load(file)
                return WorldcatAccessToken(
                    key=data["key"],
                    secret=data["secret"],
                    scopes=data["scopes"],
                    agent=data["agent"],
                )
        ```

    === "get_oclc_numbers"

        ```python
        def get_oclc_numbers(filepath: str) -> List:
            """
            Reads a file of OCLC Numbers and adds each one to a list.

            Args:
                filepath: path to location of file with OCLC Numbers

            Returns:
                oclc_numbers: a list of OCLC Numbers
            """
            oclc_numbers = []
            with open(filepath, "r") as numbers:
                for number in numbers:
                    oclc_numbers.append(number.strip("\n"))
            return oclc_numbers

        ```

### Get Full MARC records from minimal vendor data
This use case shows how to use vendor data to query WorldCat and retrieve full bibliographic records. The resulting records are saved to a new file. 

Three different approaches:

1. Given MARC records, query WorldCat using the `bib_match` method.
2. Given vendor data in a spreadsheet, form queries using the vendor data and query WorldCat using the `brief_bibs_search` method. Retrieve full MARC records using the resulting OCLC Numbers with the `bib_get` method.
3. Given vendor data in a spreadsheet, create generate MARC21 records and query WorldCat with these records using the `bib_match` method.

#### 1. MARC file and bib_match
Given minimal MARC records from a vendor, identify full MARC records for a set of books. Merge embedded order data (EOD) from vendor into the resulting full MARC records and save these records to a new file.

Use data provided in a `.mrc` file and `/bibs/match` endpoint

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate `MetadataSession`
      2. Read records from .mrc file one-by-one
      3. Extract EOD from vendor record
      4. Match record using `bib_match`
      5. Parse `.json` response and extract OCLC Number
      6. Retrieve full MARC record using OCLC Number
      7. Create pymarc Record object from resulting MARC record
      8. Merge EOD from initial file into new MARC record
      9. Write record to new `.mrc` file

```python title="MARC file and bib_match"
from bookops_worldcat import MetadataSession
from pymarc import MARCReader, MARCWriter, Record
import os

from utils import get_token  # (1)!

token = get_token(
  f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

  # Step 2.  Read records from .mrc file one-by-one
  with open("data/test_vendor_data.mrc", "rb") as file: # (2)!
      reader = MARCReader(file)
      for record in reader:

          # Step 3. Extract EOD from vendor record
          order_data = record.get("960") # (3)! 

          # Step 4. Match record using bib_match
          match_response = session.bib_match(
              record=record.as_marc(), recordFormat="application/marc"
          )

          # Step 5. Parse .json response and extract OCLC Number
          match_json = match_response.json()
          matched_oclc_number = match_json["briefRecords"][0]["oclcNumber"]

          # Step 6. Retrieve full MARC record using OCLC Number
          get_response = session.bib_get(
              matched_oclc_number, responseFormat="application/marc"
          )

          # Step 7. Create pymarc Record object from resulting MARC record
          pymarc_record = Record(get_response.content)

          # Step 8. Merge EOD from initial file into new MARC record
          pymarc_record.add_field(order_data)

          # Step 9. Write record to new .mrc file
          writer = MARCWriter(open("data/Example1_output.mrc", "ab"))
          writer.write(pymarc_record)
          writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of your vendor MARC file here
3. Change MARC tag for EOD (or add additional fields) based on local practices

#### 2. Spreadsheet data and brief_bibs_search
Search for records using data provided in a spreadsheet and `/search/brief-bibs/` endpoint. Retrieve full MARC records with the resulting OCLC numbers. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:

      1. Initiate `MetadataSession`
      2. Read data from spreadsheet
      3. Form query using data from spreadsheet. Use `brief_bibs_search` and provided data: title, author, pub date, ISBN, etc.
      4. Parse response and identify OCLC Numbers to use to retrieve records
      5. Retrieve full MARC records

```python title="Spreadsheet data and brief_bibs_search"
from bookops_worldcat import MetadataSession
from pymarc import MARCWriter, Record, Field, Subfield
import os
import csv

from utils import get_token # (1)!

token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

    # Step 2.  Read data from spreadsheet
    with open("data/test_vendor_data.csv", "r", encoding="utf-8") as csvfile: # (2)!
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader)

        # Step 3. Iterate through each row in spreadsheet
        for row in reader:

            # Step 4. Form query using spreadsheet data including title, author, pub 
            # date, and ISBN. Use brief_bibs_search search for records.
            brief_bib_response = session.brief_bibs_search(
                q=f"ti:{row[0]} AND au:{row[1]} AND bn:{row[2]}",
                inCatalogLanguage="eng",
                itemSubType="book-printbook",
                datePublished=row[3], # (3)!
            )

            # Step 5. Parse .json response and extract OCLC Number
            brief_bib_json = brief_bib_response.json()
            print(brief_bib_json)
            matched_oclc_number = brief_bib_json["briefRecords"][0]["oclcNumber"]

            # Step 6. Retrieve full MARC record using OCLC Number
            get_response = session.bib_get(
                matched_oclc_number, responseFormat="application/marc"
            )

            # Step 7. Create pymarc Record object from resulting MARC record
            pymarc_record = Record(get_response.content)

            # Step 8. Merge EOD from initial file into new MARC record
            pymarc_record.add_field(
                Field(
                    tag="949",
                    indicators=["", ""],
                    subfields=[
                        Subfield(code="i", value=f"{row[4]}"), # (4)!
                        Subfield(code="p", value=f"{row[5]}"), # (5)!
                    ],
                )
            )

            # Step 9. Write record to new .mrc file
            writer = MARCWriter(open("data/Example2_output.mrc", "ab"))
            print(pymarc_record)
            writer.write(pymarc_record)
            writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of your vendor spreadsheet file here.
3. The spreadsheet contains the the following fields: TITLE, AUTHOR, ISBN, PUB_DATE, BARCODE, ITEM_PRICE
4. 949$i is the barcode
5. 949$p is the item price

#### 3. Converted spreadsheet data and bib_match
Convert data from spreadsheet into MARC records and match records using /bibs/match endpoint. Retrieve resulting records, add local fields, and save records to new file.

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate MetadataSession
      2. Read data from spreadsheet
      3. Iterate through each row in spreadsheet
      4. Create record from row of spreadsheet data
      5. Match record using bib_match
      6. Parse .json response and extract OCLC Number
      7. Retrieve full MARC record using OCLC Number
      8. Create pymarc Record object from resulting MARC record
      9. Merge EOD from initial file into new MARC record
      10. Write record to new .mrc file

```python title="Converted spreadsheet data and bib_match"
from bookops_worldcat import MetadataSession
from pymarc import MARCWriter, Record, Field, Subfield
import os
import csv

from utils import get_token # (1)!

token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

    # Step 2.  Read data from spreadsheet
    with open("data/test_vendor_data.csv", "r", encoding="utf-8") as csvfile:  # (2)!
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader)

        # Step 3. Iterate through each row in spreadsheet
        for row in reader:

            # Step 4. Create record from row of spreadsheet data
            record = Record(leader="00000nam a2200000u  4500") # (3)!
            record.add_field(
                Field(
                    tag="008",
                    data="240424|||||||||xx#|||||||||||||||0|||||u", # (4)!
                ),
                Field(
                    tag="020",
                    indicators=[" ", " "],
                    subfields=[Subfield(code="a", value=f"{row[2]}")], # (5)!
                ),
                Field(
                    tag="100",
                    indicators=["0", " "],
                    subfields=[Subfield(code="a", value=f"{row[1]}")], # (6)!
                ),
                Field(
                    tag="245",
                    indicators=["1", " "],
                    subfields=[Subfield(code="a", value=f"{row[0]}")], # (7)!
                ),
                Field(
                    tag="264",
                    indicators=[" ", "1"],
                    subfields=[Subfield(code="c", value=f"{row[3]}")], # (8)!
                ),
            )

            # Step 5. Match record using bib_match
            match_response = session.bib_match(
                record=record.as_marc(), recordFormat="application/marc"
            )

            # Step 6. Parse .json response and extract OCLC Number
            match_json = match_response.json()
            matched_oclc_number = match_json["briefRecords"][0]["oclcNumber"]

            # Step 7. Retrieve full MARC record using OCLC Number
            get_response = session.bib_get(
                matched_oclc_number, responseFormat="application/marc"
            )

            # Step 8. Create pymarc Record object from resulting MARC record
            pymarc_record = Record(get_response.content)

            # Step 9. Merge EOD from initial file into new MARC record
            pymarc_record.add_field(
                Field(
                    tag="949",
                    indicators=["", ""],
                    subfields=[
                        Subfield(code="i", value=f"{row[4]}"),  # (9)!
                        Subfield(code="p", value=f"{row[5]}"),  # (10)!
                    ],
                )
            )

            # Step 10. Write record to new .mrc file
            writer = MARCWriter(open("data/Example3_output.mrc", "ab"))
            writer.write(pymarc_record)
            writer.close()

```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of your vendor spreadsheet file here.
3. Create a generic Leader.
4. Create a generic 008.
5. Add the ISBN from the spreadsheet
6. Add the Author from the spreadsheet
7. Add the Title from the spreadsheet
8. Add the date of publication from the spreadsheet
9. Add the barcode from the spreadsheet
10. Add the price from the spreadsheet

### Check and Set/Unset Holdings
#### 1. Using OCLC Numbers
Read OCLC Numbers from a text file and check if holdings are set. Set holdings using OCLC Number. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Read OCLC Numbers from file
      2. Initiate MetadataSession
      3. Loop through OCLC Numbers
      4. Check if holdings are set using OCLC Number
      5. Set holdings using OCLC Number
      6. Unset holdings using OCLC Number

```python title="Using OCLC Numbers"
import os
from bookops_worldcat import MetadataSession

from utils import get_token, get_oclc_numbers  # (1)!


token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# 1. Read OCLC Numbers from file
oclc_numbers = get_oclc_numbers("data/NYPLtestOclcNumbers.txt")  # (2)!
# 2. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 3. Loop through OCLC Numbers
    for number in oclc_numbers:
        # 4. Check if holdings are set using OCLC Number
        response = session.holdings_get_current(number)
        print(response.json())

        # 5. Set holdings using OCLC Number
        response = session.holdings_set(number)
        print(response.json())

        # 6. Unset holdings using OCLC Number
        response = session.holdings_unset(number)
        print(response.json())
```

1. The helper functions, `get_token` and `get_oclc_numbers`, are mentioned at the top of this page. In this example we are importing them from another module, `utils.py`
2. Enter the name of the .txt file with your OCLC numbers here.

#### 2. Using MARC records
Read MARC records from a .mrc file, extract the OCLC number from the records and check if holdings are set. Set holdings using the MARC record. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate MetadataSession


### Get classification recommendations for vendor records
Read data from a .mrc file and query WorldCat to retrieve classification recommendations. Add the resulting call numbers to the MARC records and write the records to a new .mrc file.

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate MetadataSession

### Manage Retention Commitments with Local Holdings Records

