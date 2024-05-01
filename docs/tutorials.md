# Tutorials
The following examples illustrate how bookops-worldcat can be used in technical services workflows. These examples use [pymarc](https://pymarc.readthedocs.io/en/latest/) (version 5.1.2) and modules from the Python standard library in addition to bookops-worldcat. 

Each example contains in-line comments in the code explaining the process step-by-step.

### Setup
#### Create and activate a virtual environment
Create and activate a virtual environment before installing any packages. Using a virtual environment can help users manage dependencies. For more information about virtual environments see [PyPA's guide to virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) and [Real Python's Virtual Environments primer](https://realpython.com/python-virtual-environments-a-primer/).

Windows (Git Bash):

1. Create your virtual environment

    `python -m venv .venv`

2. Activate your virtual environment
   
    `source ./.venv/scripts/activate`

3. Install tutorial packages
   
    `pip -m install bookops-worldcat`

    `pip -m install pymarc`

MacOS: 

1. Create a virtual environment
    
    `python3 -m venv .venv`

2. Activate your virtual environment

    `source ./.venv/bin/activate`

3. Install tutorial packages

    `pip3 -m install bookops-worldcat`

    `pip3 -m install pymarc`


### Obtain an Access Token
The examples below use the following helper function to get an Access Token:

```python title="get_token helper function"
def get_token(filepath: str) -> WorldcatAccessToken:
   """
   Retrieves user's WSKey credentials from a .json file.

   Args:
       filepath: 
            Path to location of .json file with credentials.
            The format of the credentials in the .json file should be:
               {
                 "key": "my_key",
                 "secret": "my_secret",
                 "scopes": "WorldcatMetadataAPI",
                 "agent": "MyApp/1.0"
               } 

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


### Match minimal vendor records to full WorldCat records 
Given minimal MARC records from a vendor, identify matches in WorldCat using the `/manage/bibs/match` endpoint. Parse the API response and retrieve full MARC records using the `/manage/bibs` endpoint. Merge the resulting records with the original records and save them to a new file. 

```python title="Match MARC records"
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader, MARCWriter, Record

from utils import get_token  # (1)!

token = get_token("C:/Users/username/credentials/tutorial_creds.json") # (2)!

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

  # Step 2.  Read records from .mrc file one-by-one
  with open("data/tutorial_input_1.mrc", "rb") as file: # (3)!
      reader = MARCReader(file)
      for record in reader:

          # Step 3. Extract embedded order data from vendor record
          order_data = record.get("960") # (4)! 

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

          # Step 7. Create pymarc Record object from MARC record in API response
          pymarc_record = Record(get_response.content)

          # Step 8. Merge order data from original record into new MARC record
          pymarc_record.add_field(order_data)

          # Step 9. Write record to new .mrc file
          writer = MARCWriter(open("data/tutorial_output_1.mrc", "ab"))
          writer.write(pymarc_record)
          writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from a module named `utils.py`
2. The filepath for the `.json` file where your WSKey is stored.
3. This is the name of the vendor MARC file.
4. This is a MARC tag used for embedded order data but users should change this field based on local practices.


### Search brief bibliographic resources
Given minimal data in a spreadsheet, read data to form queries. Search for records using the `/search/brief-bibs/` endpoint and query formed from spreadsheet data. Retrieve full MARC records using the OCLC numbers in the API response. 

The spreadsheet in this example contains the following fields: Title, Author, ISBN, Publication Date, Barcode, and Item Price.

```python title="Search brief bibliographic resources"
import os
import csv

from bookops_worldcat import MetadataSession
from pymarc import MARCWriter, Record, Field, Subfield

from utils import get_token # (1)!

token = get_token("C:/Users/username/credentials/tutorial_creds.json") # (2)!

# Step 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:

    # Step 2.  Read data from spreadsheet
    with open("data/tutorial_input_2.csv", "r", encoding="utf-8") as csvfile:  # (3)!
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader)

        # Step 3. Iterate through each row in spreadsheet
        for row in reader:

            # Step 4. Query API using spreadsheet data and brief_bibs_search 
            brief_bib_response = session.brief_bibs_search(
                q=f"ti:{row[0]} AND au:{row[1]} AND bn:{row[2]}",
                inCatalogLanguage="eng",
                itemSubType="book-printbook",
                datePublished=row[3], # (4)!
            )

            # Step 5. Parse .json response and extract OCLC Number
            brief_bib_json = brief_bib_response.json()
            matched_oclc_number = brief_bib_json["briefRecords"][0]["oclcNumber"]

            # Step 6. Retrieve full MARC record using OCLC Number
            get_response = session.bib_get(
                matched_oclc_number, responseFormat="application/marc"
            )

            # Step 7. Create pymarc Record object from MARC record in API response
            pymarc_record = Record(get_response.content)

            # Step 8. Merge additional data from spreadsheet into new MARC record
            pymarc_record.add_field(
                Field(
                    tag="949",
                    indicators=["", ""],
                    subfields=[
                        Subfield(code="i", value=f"{row[4]}"), # (5)!
                        Subfield(code="p", value=f"{row[5]}"), # (6)!
                    ],
                )
            )

            # Step 9. Write record to new .mrc file
            writer = MARCWriter(open("data/tutorial_output_2.mrc", "ab"))
            writer.write(pymarc_record)
            writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from a module named `utils.py`
2. The filepath for the `.json` file where your WSKey is stored.
3. The name of your vendor spreadsheet file.
4. The query is formed using data from the first four columns of the spreadsheet: Title (column 1), Author (column 2), Publication Date (column 3), and ISBN (column 4)
5. Add the barcode to the 949$i field.
6. Add the item price to the 949$p field.

### Check and Set Holdings
#### Using MARC records
Given a file of MARC records, extract the OCLC numbers from the records and check if holdings are set. Set/Unset holdings using the MARC record. 

```python title="Using MARC records"
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader

from utils import get_token  # (1)!


token = get_token("C:/Users/username/credentials/tutorial_creds.json") # (2)!

# 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 2. Read MARC records from file
    with open("data/tutorial_input_3.mrc", "rb") as marc_file:  # (3)!
        reader = MARCReader(marc_file)
        for record in reader:
            # 3. Get OCLC Number for record
            oclc_number = record.get("035").value()

            # 4. Check if holdings are set for record
            get_response = session.holdings_get_current(oclc_number)

            # 5.1. Set holdings with record
            set_response = session.holdings_set_with_bib( # (4)!
                record.as_marc(), recordFormat="application/marc"
            )

            # 5.2. Unset holdings with record
            unset_response = session.holdings_unset_with_bib( # (5)!
                record.as_marc(), recordFormat="application/marc"
            )
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from a module named `utils.py`
2. The filepath for the `.json` file where your WSKey is stored.
3. The name of the file with your MARC records.
4. If copying code from this example, delete step 5.1 or 5.2 depending on whether you would like to set or unset holdings. 
5. If copying code from this example, delete step 5.1 or 5.2 depending on whether you would like to set or unset holdings.

#### Using OCLC Numbers
Read OCLC Numbers from a text file and check if holdings are set. Set/unset holdings using OCLC Number. 

??? info "Step-by-step instructions"
    This example uses the following steps. These steps are noted using in-line comments in the code:
    
      1. Read a file of OCLC Numbers and add them to a list.
      2. Initiate `MetadataSession`
      3. Loop through OCLC Numbers.
      4. Check if holdings are set using OCLC Number.
      5. Set holdings using OCLC Number.
      6. Unset holdings using OCLC Number.

```python title="Using OCLC Numbers"
import os

from bookops_worldcat import MetadataSession

from utils import get_token  # (1)!


token = get_token("C:/Users/username/credentials/tutorial_creds.json") # (2)!

# 1. Read a file of OCLC Numbers and add them to a list
oclc_numbers = []
with open("data/tutorial_input_3.txt", "r") as numbers:  # (3)!
    for number in numbers:
        oclc_numbers.append(number.strip("\n"))
# 2. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 3. Loop through OCLC Numbers
    for number in oclc_numbers:
        # 4. Check if holdings are set using OCLC Number
        get_response = session.holdings_get_current(number)

        # 5.1. Set holdings using OCLC Number
        set_response = session.holdings_set(number) # (4)!

        # 5.2. Unset holdings using OCLC Number
        unset_response = session.holdings_unset(number) # (5)!
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from a module named `utils.py`
2. The filepath for the `.json` file where your WSKey is stored.
3. The name of the `.txt` file with your OCLC numbers.
4. If copying code from this example, delete step 5.1 or 5.2 depending on whether you would like to set or unset holdings. 
5. If copying code from this example, delete step 5.1 or 5.2 depending on whether you would like to set or unset holdings.


### Get classification recommendations for vendor records
Read data from a `.mrc` file and query WorldCat to retrieve classification recommendations. Add the resulting call numbers to the original MARC records and write the records to a new `.mrc` file.

```python title="Get classification recommendations"
import os

from bookops_worldcat import MetadataSession
from pymarc import MARCReader, Field, Subfield, MARCWriter

from utils import get_token  # (1)!


token = get_token("C:/Users/username/credentials/tutorial_creds.json") # (2)!

# 1. Initiate MetadataSession
with MetadataSession(authorization=token) as session:
    # 2. Read MARC records from file
    with open("data/classification_tutorial.mrc", "rb") as marc_file:  # (3)!
        reader = MARCReader(marc_file)
        for record in reader:
            # 3. Extract OCLC Number from record
            oclc_number = record.get("035").value()

            # 4. Query API for classification recommendations using OCLC Number
            response = session.bib_get_classification(oclc_number)

            # 5. Parse API response
            dewey = response.json()["dewey"]["mostPopular"][0]
            lcc = response.json()["lc"]["mostPopular"][0]

            # 6. Add classification from response to records
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
            writer = MARCWriter(open("data/tutorial_output_4.mrc", "ab"))
            writer.write(record)
            writer.close()
```

1. The helper function, `get_token`, is mentioned at the top of this page. In this example we are importing it from a module named `utils.py`
2. The filepath for the `.json` file where your WSKey is stored.
3. The name of the file with your MARC records.