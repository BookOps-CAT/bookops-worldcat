## Tutorials

```py title="oclc number"
with MetadataSession(authorization=token) as session:
    result = session.bib_get_current_oclc_number("992611164")
    print(result.status_code)
    print(result.url)
200
"https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers=992611164"
```

