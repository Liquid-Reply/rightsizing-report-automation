"""
This module holds the logic to manipulate resources inside an specific project.
The summary page for every project is also processed here.
The Project class contains all the logic needed to create a complete
report (contains multiple sheets) for a specific project

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""


from copy import deepcopy
import os
import pandas as pd

from finops_report_automation.resource import Resource
from .excel_writer import write_resource_sheet, write_summary_sheet, write_cross_project_sheet
from .messages_helper import label
from .constants import GENERAL_SHEET_CONFIGURATION

CONFIG_PATH = os.environ.get("CONFIG_PATH") or "./config"
REPORTINGS_PATH = os.environ.get("REPORTINGS_PATH", "./reports")


class Project:
    def __init__(self, name, account_ids, amortized_costs_raw):
        self.name = name
        self.account_ids = account_ids
        self.amortized_costs_raw = amortized_costs_raw
        self.resources = []
        self.amortized_costs_df = self.json_to_dataframe()
        self.summary = pd.DataFrame
        self.sum = pd.DataFrame


    def __str__(self):
        return f"""
        Project Name: {self.name}
        Related Accounts: {self.account_ids}
        Resources: {[resource.name for resource in self.resources]}
        """

    def append_resource(self, product, api_data, account_ids, account_details):
        resource = Resource(
            product,
            api_data,
            account_ids,
            account_details
        )
        if not resource.df.empty:
            self.resources.append(resource)
            self.create_summary()
            self.sum_all_accounts()

    def write_report(self, dst_folder: str) -> str:
        """
        This functions calls the write functions for both the individual
        resource sheets (EC2, RDS, EBS, S3) as well as the summary sheet.
        """
        if len(self.resources) >= 1:
            filename = f"{dst_folder}/{self.name}.xlsx"
            with pd.ExcelWriter(filename, mode="w") as writer:
                write_summary_sheet(
                    writer, "General", self.name, self.summary, self.sum,
                )
                for resource in self.resources:
                    write_resource_sheet(
                        writer, resource.name.upper(), resource
                    )
            return filename
        return ""

    def json_to_dataframe(self) -> pd.DataFrame:
        """
        Parse the raw json data from the API to a dataframe.
        Returns a dataframe.
        """
        df = pd.json_normalize(
            self.amortized_costs_raw,
            "dimensions"
        )
        df2 = pd.json_normalize(
            self.amortized_costs_raw,
            "metrics",
        )
        df = df.merge(df2["sum"], right_index=True, left_index=True)
        df[0] = df[0].apply(lambda x: x.replace('-', ''))
        return df

    def add_summary_row(self, amortized_cost, resource_type, account_id, action) -> list:
        """
        Create a single row for the summary sheet.
        Returns a list ready to be appended to a dataframe
        """
        summary = []
        df = resource_type.df.loc[resource_type.df["recommendations_action"] == action]
        df = df.loc[df["vendorAccountId"] == account_id]
        resource_copy = deepcopy(resource_type)
        resource_copy.df = df
        if df.empty:
            return []
        message_df = label(
            resource_copy, resource_copy.recommendation_summary(action.lower()), action.lower())
        message_str = message_df["message"].iloc[0]
        saving_column = "recommendations_savings"
        if resource_copy.name == "rds":
            saving_column = "topSavings"
        best_recommendation_savings = resource_copy.get_best_recommendation(df)[
            saving_column].values[0]
        monthly_savings = df[saving_column].sum()
        annual_savings = monthly_savings * 12
        account_name = df.loc[df['vendorAccountId'] ==
                              account_id]['vendorAccountName'].values[0]

        summary = [
            account_id,
            account_name,
            resource_type.name.upper(),
            action,
            float(best_recommendation_savings),
            float(monthly_savings),
            float(annual_savings),
            float(amortized_cost),
            (float(monthly_savings)/float(amortized_cost)),
            message_str
        ]
        return summary

    def create_summary(self):
        """
        Creates the summary page of the report based on the
        resources listed on this instance.
        Returns a dataframes ready for writing to an excel file.
        """
        cols = GENERAL_SHEET_CONFIGURATION["column_mapping"].keys()
        summary_df = pd.DataFrame(columns=cols)
        for resource_type in self.resources:
            for action in ["Terminate", "Rightsize"]:
                for account_id in self.account_ids:
                    if resource_type.df['vendorAccountId'].isin([account_id]).any().any():
                        amortized_cost = self.amortized_costs_df.loc[
                            self.amortized_costs_df[0] == account_id]['sum'].values[0]
                        row = self.add_summary_row(
                            amortized_cost, resource_type, account_id, action)
                        if len(row) > 0:
                            summary_df.loc[len(summary_df)] = row
        self.summary = summary_df


    def sum_all_accounts(self):
        """
        Calculates the total monthly saving potential, annual savings potential,
        cost and cost to savings relation per project.
        Returns a dataframe.
        """     
        relevant_account_ids = []
        for account_id in self.account_ids:
            for resource_type in self.resources:
                if resource_type.df['vendorAccountId'].isin([account_id]).any().any():
                    relevant_account_ids.append(account_id)
        amortized_cost = self.amortized_costs_df.loc[self.amortized_costs_df[0].isin(
            relevant_account_ids)]
        cost = amortized_cost['sum'].astype(float).sum()

        annual_savings_potential = self.summary["annualSavings"].sum()
        monthly_saving_potential = self.summary["monthlySavings"].sum()
        relation = float(monthly_saving_potential) / float(cost)
        df = pd.DataFrame([[monthly_saving_potential, annual_savings_potential, cost, relation]], columns=[
                          "monthly_saving_potential", "annual_savings_potential", "cost", "relation"])
        self.sum = df


def create_project_id_mapping() -> pd.DataFrame:
    """
    Create Dataframe from static account mapping.
    """
    df = pd.read_excel(
        f"{CONFIG_PATH}/accountMapping.xlsx",
        names=["projectName", "vendorAccountId"],
        skiprows=2,
        usecols="A:B",
        header=None,
    )
    return df

def create_projects(amortized_cost_raw):
    """
    Create class Project instances.
    """
    projects = []
    df = create_project_id_mapping()
    # Extract unique project names
    for name in df["projectName"].unique():
        # Hacky way to mimic dict behaviour. Improvements?
        account_ids = df.loc[df["projectName"] == name]["vendorAccountId"].to_list()
        projects.append(Project(name, account_ids, amortized_cost_raw["rows"]))

    return projects

def create_cross_project_overview(dataframes_list) -> str:
    """
    Creates and writes the cross project overview. 
    """
    cross_project_summary = pd.concat(dataframes_list)
    project_id_df = create_project_id_mapping()
    cross_project_summary = project_id_df.merge(cross_project_summary, on="vendorAccountId")
    filepath = f"{REPORTINGS_PATH}/cross_project_overview.xlsx"

    with pd.ExcelWriter(filepath, mode="w") as writer:
        write_cross_project_sheet(writer, "General", cross_project_summary)
    return filepath

