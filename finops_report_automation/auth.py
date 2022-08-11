"""
Module that checks if the API key is already configured on the environment. Raises error if not

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""
import os
from .errors import ApiTokenError


def get_api_key():
    if os.environ.get("API_KEY") is not None:
        return os.environ.get("API_KEY")
    else:
        raise ApiTokenError("Api Token not configured. Please get an API token")
