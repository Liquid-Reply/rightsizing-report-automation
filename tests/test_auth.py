"""
Module to test all related auth functions

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""
import os
import unittest
from unittest import mock

import finops_report_automation.auth as auth
from finops_report_automation.errors import ApiTokenError


class TestAuth(unittest.TestCase):
  def test_get_missing_token(self):
    self.assertRaises(ApiTokenError, auth.get_api_key)

  # This mocks an API_KEY to ensure that our getter function
  # is correctly retrieving the key
  @mock.patch.dict(os.environ, {"API_KEY": "123KEY"})
  def test_get_token(self):
    token = auth.get_api_key()
    self.assertTrue(len(token))
