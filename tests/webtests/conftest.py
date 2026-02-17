import json
import os
from typing import Generator

import pytest

from bookops_worldcat import WorldcatAccessToken


@pytest.fixture(scope="package")
def live_keys() -> Generator[None, None, None]:
    if not os.getenv("GITHUB_ACTIONS"):
        fh = os.path.expanduser("~/.oclc/nyp_wc_test.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["WCKey"] = data["key"]
            os.environ["WCSecret"] = data["secret"]
            os.environ["WCScopes"] = data["scopes"]
            yield
    else:
        yield
    os.environ.pop("WCKey")
    os.environ.pop("WCSecret")
    os.environ.pop("WCScopes")


@pytest.fixture(scope="module")
def live_token() -> Generator[WorldcatAccessToken, None, None]:
    """
    Gets live token from environment variables. For use with live tests so that
    the service does not need to request a new token for each test.
    """
    yield WorldcatAccessToken(
        key=os.environ["WCKey"],
        secret=os.environ["WCSecret"],
        scopes=os.environ["WCScopes"],
    )
