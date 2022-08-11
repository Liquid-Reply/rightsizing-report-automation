"""
Module to test all related api functions

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

import unittest
import os

from unittest import mock
from finops_report_automation.api import Api


class TestApi(unittest.TestCase):

  # This mocks an API_KEY to ensure that our getter function
  # is correctly retrieving the key
  @mock.patch.dict(os.environ, {"API_KEY": "123KEY"})
  def test_wrong_request(self):
      api = Api("http://badUrl.com")
      self.assertTrue({} == api.request("/badPath"))
