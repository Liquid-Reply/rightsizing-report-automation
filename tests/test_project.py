"""
:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

import pytest
import pandas as pd
import numpy as np
import json
from finops_report_automation.project import Project
from finops_report_automation.resource import Resource

TEST_DATA_DIR="tests/test_data"

def read_mock_excel_report(filename):
    df = pd.read_excel(filename)
    try: 
        df["vendorAccountId"] = df["vendorAccountId"].astype(str)
    except KeyError:
        print("No vendorAccountId to convert.")
    return df


@pytest.fixture
def make_project_instance():
    """
    Fixture factory. Reference:
    https://docs.pytest.org/en/6.2.x/fixture.html#factories-as-fixtures
    """
    def _make_project_instance():
        with open(f"{TEST_DATA_DIR}/project_test.json", "r") as json_data:
            config = json.load(json_data)
            project = Project(
              config["name"],
              config["account_ids"],
              config["amortized_cost"])
            resource = Resource(
              config["resources"]["product"],
              config["resources"]["api_data"],
              config["resources"]["account_ids"],
              config["resources"]["account_details"]) 
        project.resources.append(resource)
        return project
    return _make_project_instance


def test_project(make_project_instance):
    """
    Test all the sections of a project independently
    """
    project = make_project_instance()
    project.create_summary()
    summary_df = project.summary
    project.sum_all_accounts()
    sum_df = project.sum

    mock_project_summary = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_project_summary.xlsx")
    mock_project_sum = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_project_sum.xlsx")
    mock_cross_project_summary = read_mock_excel_report(f"{TEST_DATA_DIR}/mock_cross_project_summary.xlsx")

    summary_df = summary_df.sort_values(by="vendorAccountId")
    
    mock_project_summary = mock_project_summary.sort_values(by="vendorAccountId")
    summary_df.relationPotentialSavings = summary_df.relationPotentialSavings.round(5)
    mock_project_summary.relationPotentialSavings = mock_project_summary.relationPotentialSavings.round(5)
    sum_df.relation = sum_df.relation.round(5)
    mock_project_sum.relation = mock_project_sum.relation.round(5)

    project_id_df = pd.DataFrame({"projectName":["Testproject"], "vendorAccountId":["111111"]})
    cross_project_summary = project_id_df.merge(summary_df, on="vendorAccountId")    
    cross_project_summary.relationPotentialSavings = cross_project_summary.relationPotentialSavings.round(5)
    mock_cross_project_summary.relationPotentialSavings = mock_cross_project_summary.relationPotentialSavings.round(5)

    assert(np.array_equal(summary_df.values, mock_project_summary.values))        

    assert(np.array_equal(sum_df.values, mock_project_sum.values))

    assert(np.array_equal(cross_project_summary.values, mock_cross_project_summary.values))


