# Tutorials

## Save a full bib XML response to a file in MARC21 format

This recipe shows how to query Worldcat for specific full bibliographic records and save the results to a file in MARC21 format.

A conversion from the response to the MARC format is handled by the pymarc library (see more at [https://pypi.org/project/pymarc/](https://pypi.org/project/pymarc/)), specifically its `parse_xml_to_array` and `as_marc` methods.

The code below requires an access token ([`WorldcatAccessToken` object](https://bookops-cat.github.io/bookops-worldcat/0.4/#worldcataccesstoken)) to be passed to the MetadataSession for authorization.


```python
from io import BytesIO

from bookops_worldcat import MetadataSession
from pymarc import parse_xml_to_array

oclc_numbers = [850939580, 850939581, 850939582]

# obtain first an access token using the WorldcatAccessToken and 
# your OCLC Metadata API credentials

with MetadataSession(authorization=token) as session:

    for o in oclc_numbers:
        response = session.get_full_bib(oclcNumber=o)
        data = BytesIO(response.content)

        # convert into pymarc Record object
        bib = parse_xml_to_array(data)[0]

        # manipulate bib to your liking before saving to a file

        # append to a MARC21 file:
        with open("retrieved_bibs.mrc", "ab") as out:
            out.write(bib.as_marc())
```