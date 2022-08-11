"""
:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

import json


def use_offline_data(filepath):
    """
    Function used to read local json files. Mainly use is for local debugging
    """
    with open(filepath, "r") as file:
        resp = file.read()
    return json.loads(resp)
    
def write_file(filepath, data) -> str:
    """
    Write data to filesystem.
    """
    with open(filepath, "w") as file:
        file.write(data)
    return filepath