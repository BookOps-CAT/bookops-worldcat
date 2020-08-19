# -*- coding: utf-8 -*-

import requests


from . import __title__, __version__


class WorldcatAccessToken:
    """
    Requests Worldcat access token. Authenticates and authorizes using Client Credentials Grant.
    Dones not support Explicit Authorization Code and Refresh Token flows.

    Args:

    """

    def __init__(
        self, key=None, secret=None, scope=[], agent=None, timeout=None,
    ):
        """Constructor"""

        self.agent = agent
        self.grant_type = "client_credentials"
        self.key = key
        self.oauth_server = "https://oauth.oclc.org"
        self.secret = secret
        self.server_response = None
        self.timeout = timeout
        self.token_expires_at = None
        self.token_str = None
        self.token_type = None

        # default bookops-worldcat request header
        if self.agent is None:
            self.agent = f"{__title__}/{__version__}"
        else:
            if type(self.agent) is not str:
                raise TypeError("Argument 'agent' must be a string.")

        # asure passed arguments are valid
        if not self.key:
            raise ValueError("Argument 'key' is required.")
        else:
            if type(self.key) is not str:
                raise TypeError("Argument 'key' must be a string.")

        if not self.secret:
            raise ValueError("Argument 'secret' is required.")
        else:
            if type(self.secret) is not str:
                raise TypeError("Argument 'secret' must be a string.")

        if not self.timeout:
            self.timeout = (5, 5)
        else:
            if type(self.timeout) is not tuple:
                raise TypeError(
                    "Argument 'timeout' must be a tuple of two ints or floats."
                )
            else:
                for v in self.timeout:
                    try:
                        float(v)
                    except TypeError:
                        raise TypeError(
                            "Values of 'timeout' tuple must be ints or floats."
                        )
