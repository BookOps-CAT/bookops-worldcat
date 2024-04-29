# Tutorials
The following tutorials illustrate how bookops-worldcat can be used for specific use cases in technical services workflows. These examples use [pymarc](https://pymarc.readthedocs.io/en/latest/) and modules from the Python standard library in addition to bookops-worldcat. All modules or libraries used in an example are be listed as imports at the top of the code snippet. 

### Setup
#### Create and activate a virtual environment
To try the examples in this tutorial, first create and activate a virtual environment. Then install the required packages.

On PC (Git Bash):

1. Create a virtual environment

    `python -m venv .venv`

2. Activate your virtual environment
   
    `source ./.venv/scripts/activate`

3. Install tutorial packages
   
    `pip -m install bookops-worldcat`
    `pip -m install pymarc`

On Mac: 

1. Create a virtual environment
    
    `python3 -m venv .venv`

2. Activate your virtual environment

    `source ./.venv/bin/activate`

3. Install tutorial packages

    `pip3 -m install bookops-worldcat`
    `pip3 -m install pymarc`


 This tutorial uses the following helper functions. In the examples below these functions are imported from a separate `utils.py` module:

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

### Match minimal vendor records to full WorldCat records 
Given minimal MARC records from a vendor, identify matches in WorldCat using the `/manage/bibs/match` endpoint. Parse the API response and retrieve full MARC records using the `/manage/bibs` endpoint. Merge the resulting records with the original records and save them to a new file. 

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
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader, MARCWriter, Record

from utils import get_token  # (1)!

token = get_token(
  f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

  # Step 2.  Read records from .mrc file one-by-one
  with open("data/match_bibs_tutorial.mrc", "rb") as file: # (2)!
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
          writer = MARCWriter(open("data/match_bibs_output.mrc", "ab"))
          writer.write(pymarc_record)
          writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of your vendor MARC file here
3. Change MARC tag for EOD (or add additional fields) based on local practices


### Search brief bibliographic resources
Read data from a spreadsheet to form queries. Use queries to search for records using the `/search/brief-bibs/` endpoint. Retrieve full MARC records for the resulting OCLC numbers. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:

      1. Initiate `MetadataSession`
      2. Read data from spreadsheet
      3. Form query using data from spreadsheet. Use `brief_bibs_search` and provided data: title, author, pub date, ISBN, etc.
      4. Parse response and identify OCLC Numbers to use to retrieve records
      5. Retrieve full MARC records

```python title="Spreadsheet data and brief_bibs_search"
import os
import csv

from bookops_worldcat import MetadataSession
from pymarc import MARCWriter, Record, Field, Subfield

from utils import get_token # (1)!

token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

    # Step 2.  Read data from spreadsheet
    with open("data/brief_bibs_tutorial.csv", "r", encoding="utf-8") as csvfile: # (2)!
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader)

        # Step 3. Iterate through each row in spreadsheet
        for row in reader:

            # Step 4. Form query using spreadsheet data including title, 
            # author, pub date, and ISBN. Use brief_bibs_search search 
            # for records.
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
            writer = MARCWriter(open("data/brief_bibs_tutorial_output.mrc", "ab"))
            print(pymarc_record)
            writer.write(pymarc_record)
            writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of your vendor spreadsheet file here.
3. The spreadsheet contains the the following fields: TITLE, AUTHOR, ISBN, PUB_DATE, BARCODE, ITEM_PRICE
4. 949$i is the barcode
5. 949$p is the item price

### Check and Set Holdings

#### 1. Using MARC records
Read MARC records from a .mrc file, extract the OCLC number from the records and check if holdings are set. Set holdings using the MARC record. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate `MetadataSession`
      2. Read MARC records from file
      3. Get OCLC Number for record
      4. Check if holdings are set for record
      5. Set holdings with record
      6. Unset holdings with record

```python title="Using MARC records"
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader

from utils import get_token  # (1)!


token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 2. Read MARC records from file
    with open("data/holdings_tutorial_1.mrc", "rb") as marc_file:  # (2)!
        reader = MARCReader(marc_file)
        for record in reader:
            # 3. Get OCLC Number for record
            oclc_number = record.get("001").data

            # 4. Check if holdings are set for record
            response = session.holdings_get_current(oclc_number)
            print(response.json())

            # Set holdings with record
            response = session.holdings_set_with_bib(record)
            print(response.json())

            # Unset holdings with record
            response = session.holdings_unset_with_bib(record)
            print(response.json())
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of the file with your MARC records here.

#### 2. Using OCLC Numbers
Read OCLC Numbers from a text file and check if holdings are set. Set holdings using OCLC Number. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Read OCLC Numbers from file
      2. Initiate `MetadataSession`
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
oclc_numbers = get_oclc_numbers("data/holdings_tutorial_2.txt")  # (2)!
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


### Get classification recommendations for vendor records
Read data from a .mrc file and query WorldCat to retrieve classification recommendations. Add the resulting call numbers to the MARC records and write the records to a new .mrc file.

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Initiate `MetadataSession`
      2. Read MARC records from file
      3. Get OCLC Number for record
      4. Get classification recommendations based on record
      5. Parse API response
      6. Add classification to records
      7. Write records to new file

```python title="Get classification recommendations"
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader, Field, Subfield, MARCWriter

from utils import get_token  # (1)!


token = get_token(
    f"{os.path.join(os.environ['USERPROFILE'], '.oclc/tutorial_creds.json')}"
)

# 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 2. Read MARC records from file
    with open("data/classification_tutorial.mrc", "rb") as marc_file:  # (2)!
        reader = MARCReader(marc_file)
        for record in reader:
            # 3. Get OCLC Number for record
            oclc_number = record.get("001").data

            # 4. Get classification recommendations based on record
            response = session.bib_get_classification(oclc_number)
            print(response.json())

            # 5. Parse API response
            dewey = response.json()["dewey"]["mostPopular"][0]
            lcc = response.json()["lc"]["mostPopular"][0]

            # 6. Add classification to records
            record.add_field(
                Field(
                    tag="050",
                    indicators=[" ", "0"],
                    subfields=[Subfield(code="a", value=f"{lcc}")],
                )
            )
            record.add_field(
                Field(
                    tag="082",
                    indicators=["0", " "],
                    subfields=[Subfield(code="a", value=f"{dewey}")],
                )
            )

            # 7. Write records to new file
            writer = MARCWriter(open("data/classification_tutorial_output.mrc", "ab"))
            writer.write(record)
            writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from another module, `utils.py`
2. Enter the name of the file with your MARC records here.