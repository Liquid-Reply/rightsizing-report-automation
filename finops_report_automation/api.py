"""
Module that defines a generic and centralized way to query the Cloudability API

Example usage:
```
api = Api("http://api.url.com")
response = api.request("/v3/rightsizing/aws/recommendations/")
print(response)
````

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

from datetime import date, timedelta
import os
import requests
from json.decoder import JSONDecodeError

import yaml
from .auth import get_api_key

CONFIG_PATH = os.environ.get("CONFIG_PATH") or "./config"

class Api:
    def __init__(self, base_url, params={}) -> None:
        self.base_url = base_url
        self.params = params

    @property
    def api_key(self):
        return get_api_key()

    def request(self, path, params=None):
        """Use the requests module to send the request"""
        response = requests.get(
          f"{self.base_url}{path}",
          params=params,
          auth=(self.api_key, "")
        )
        try:
            return response.json()
        except JSONDecodeError:
            return {}


    def get_accounts(self):
        """
        Calls the CloudAbility Accounts API. Returns all information about the
        linked accounts. This is needed because the Rightsizing API does not
        return the account names.
        """

        resp = self.request("/v3/vendors/AWS/accounts")
        return resp


    def get_rightsizing(self, config):
        """
        Calls the CloudAbility Rightsizing API. Returns resources that have a
        rightsizing / termination recommendation. Depending on the configuration
        file this will either return ec2, ebs, s3 or rds results.
        """

        resp = self.request(
            f'/v3/rightsizing/aws/recommendations/{config["product"]}', config)
        return resp


    def get_amortized_cost(self):
        """
        Calls the CloudAbility Reporting API.
        """
        with open(f"{CONFIG_PATH}/amortized_cost_config.yaml", "r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        config["end"] = str(date.today())
        config["start"] = str(date.today() - timedelta(days=29))

        resp = self.request(
            "/v3/internal/reporting/cost/run", config)
        return (resp)                
