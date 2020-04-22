ORD_MAP = {"ascending": "", "descending": ",,0"}

KEY_MAP = {
    "relevance": "relevance",
    "title": "Title",
    "author": "Author",
    "date": "Date",
    "library_count": "LibraryCount",
    "score": "Score",
}

HOLDINGS_RESPONSE_FORMATS = {
    "xml": "application/atom+xml",
    "json": "application/atom+json",
}

# fmt: off
# this is not a full list
# see more at:
# https://help.oclc.org/Librarian_Toolbox/Searching_WorldCat_Indexes
SRU_INDICES = {
    "au": {
        "label": "author",
        "service_level": "default",
        "limit_only": False},
    "pc": {
        "label": "DLC only",
        "service_level": "full",
        "limit_only": True},
    "ti": {
        "label": "title",
        "service_level": "default",
        "limit_only": False},
    "bn": {
        "label": "ISBN",
        "service_level": "default",
        "limit_only": False},
    "in": {
        "label": "ISSN",
        "service_level": "default",
        "limit_only": False},
    "kw": {
        "label": "keyword",
        "service_level": "default",
        "limit_only": False},
    "la": {
        "label": "languge (primary coded)",
        "service_level": "default",
        "limit_only": True},
    "dn": {
        "label": "LCCN",
        "service_level": "default",
        "limit_only": False},
    "li": {
        "label": "library holdings",
        "service_level": "default",
        "limit_only": True},
    "mt": {
        "label": "material type",
        "service_level": "default",
        "limit_only": True},
    "pb": {
        "label": "publisher",
        "service_level": "full",
        "limit_only": False},
    "mn": {
        "label": "music/publisher number",
        "service_level": "full",
        "limit_only": False},
    "no": {
        "label": "OCLC number",
        "service_level": "default",
        "limit_only": False},
    "se": {
        "label": "series",
        "service_level": "full",
        "limit_only": False},
    "sn": {
        "label": "standard number",
        "service_level": "full",
        "limit_only": False},
    "yr": {
        "label": "year",
        "service_level": "default",
        "limit_only": True},
}
# fmt: on
