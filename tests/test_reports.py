"""
:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

import pytest
import pandas as pd
import numpy as np
import json
from finops_report_automation.resource import Resource

TEST_DATA_DIR="tests/test_data"

def read_mock_excel_report(filename):
    df = pd.read_excel(filename)
    df["vendorAccountId"] = df["vendorAccountId"].astype(str)
    return df


@pytest.fixture
def make_resource_instance():
    """
    Fixture factory. Reference:
    https://docs.pytest.org/en/6.2.x/fixture.html#factories-as-fixtures
    """
    def _make_resource_instance(name):
        with open(f"{TEST_DATA_DIR}/{name}_test.json", "r") as json_data:
            config = json.load(json_data)
            return Resource(
              config["product"],
              config["api_data"],
              config["account_ids"],
              config["account_details"])
    return _make_resource_instance


def test_s3(make_resource_instance):
    """
    Test the creation of all the sections inside a S3 resource
    independently
    """
    s3 = make_resource_instance("s3")
    mock_s3_accounts = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_s3_accounts.xlsx")
    mock_s3_df = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_s3_records.xlsx")
    mock_s3_recommendations = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_s3_recommendations.xlsx")

    # Account assertion
    s3_accounts = s3.affected_accounts().sort_values(by="vendorAccountId")
    mock_s3_accounts = mock_s3_accounts.sort_values(by="vendorAccountId")
    assert(np.array_equal(s3_accounts.values, mock_s3_accounts.values))

    # Recommendations assertion
    s3_recommendations_rightsize = s3.recommendation_summary(action="rightsize")
    s3_recommendations_terminate = s3.recommendation_summary(action="terminate")
    s3_recommendations = pd.concat([s3_recommendations_rightsize, s3_recommendations_terminate])
    s3_recommendations = s3_recommendations.sort_values(by="vendorAccountId")
    mock_s3_recommendations = mock_s3_recommendations.sort_values(by="vendorAccountId")
    assert(np.array_equal(s3_recommendations.values, mock_s3_recommendations.values))

    # Records assertion
    s3_df2 = s3.df.sort_values(by="vendorAccountId")
    mock_s3_df = mock_s3_df.sort_values(by="vendorAccountId")
    assert(np.array_equal(s3_df2.values, mock_s3_df.values))


def test_ec2(make_resource_instance):
    """
    Test the creation of all the sections inside a EC2 resource
    independently
    """
    ec2 = make_resource_instance("ec2")
    mock_accounts = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ec2_accounts.xlsx")
    mock_recommendations = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ec2_recommendations.xlsx")
    mock_df = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ec2_records.xlsx")

    # Account assertion
    ec2_accounts = ec2.affected_accounts().sort_values(by="vendorAccountId")
    mock_accounts = mock_accounts.sort_values(by="vendorAccountId")
    assert(np.array_equal(ec2_accounts.values, mock_accounts.values))

    # Recommendations assertion
    ec2_recommendations_rightsize = ec2.recommendation_summary(action="rightsize")
    ec2_recommendations_terminate = ec2.recommendation_summary(action="terminate")
    ec2_recommendations = pd.concat([ec2_recommendations_rightsize, ec2_recommendations_terminate])
    ec2_recommendations = ec2_recommendations.sort_values(by="vendorAccountId")
    mock_recommendations = mock_recommendations.sort_values(by="vendorAccountId")
    assert(np.array_equal(ec2_recommendations.values, mock_recommendations.values))

    # Records assertion
    ec2_df2 = ec2.df.sort_values(by="vendorAccountId")
    mock_df = mock_df.sort_values(by="vendorAccountId")
    assert(np.array_equal(ec2_df2.values, mock_df.values))


def test_ebs(make_resource_instance):
    """
    Test the creation of all the sections inside a EC2 resource
    independently
    """
    ebs = make_resource_instance("ebs")
    mock_accounts = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ebs_accounts.xlsx")
    mock_recommendations = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ebs_recommendations.xlsx")
    mock_df = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_ebs_records.xlsx")

    # Account assertion
    ebs_accounts = ebs.affected_accounts().sort_values(by="vendorAccountId")
    mock_accounts = mock_accounts.sort_values(by="vendorAccountId")
    assert(np.array_equal(ebs_accounts.values, mock_accounts.values))

    # Recommendations assertion
    ebs_recommendations_rightsize = ebs.recommendation_summary(action="rightsize")
    ebs_recommendations_terminate = ebs.recommendation_summary(action="terminate")
    ebs_recommendations = pd.concat([ebs_recommendations_rightsize, ebs_recommendations_terminate])
    ebs_recommendations = ebs_recommendations.sort_values(by="vendorAccountId")
    mock_recommendations = mock_recommendations.sort_values(by="vendorAccountId")
    assert(np.array_equal(ebs_recommendations.values, mock_recommendations.values))

    # Records assertion
    ebs_df2 = ebs.df.sort_values(by="vendorAccountId")
    mock_df = mock_df.sort_values(by="vendorAccountId")
    assert(np.array_equal(ebs_df2.values, mock_df.values))
