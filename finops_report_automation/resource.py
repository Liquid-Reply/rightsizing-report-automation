"""
Module used to hold cloud resources representation. Each resource should be
able to generate it's own resumed recommendation section

Example usage:
```
ec2 = Resource("ec2", raw_data, account_ids)

# Generate the dataframes used to create the report based on the API response
affected_accounts = ec2.get_affected_accounts()
termination = ec2.recommendation_summary(action="terminate")
rightsizing = ec2.recommendation_summary(action="rightsize")
```

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbHk
"""
import pandas as pd
from .constants import (
    EC2_CONFIGURATION, RDS_CONFIGURATION, S3_CONFIGURATION, EBS_CONFIGURATION
)


class Resource:
    def __init__(
        self,
        name,
        raw_data: list,
        account_ids: list,
        account_details
    ) -> None:
        self.name = name
        self.raw_data = raw_data
        self.account_ids = account_ids
        self.account_details = account_details
        self.configuration = self.configure_resource()
        # self.recommendation = self.configure_recommendation()
        self.df = self.json_to_dataframe()

    def configure_resource(self) -> dict:
        """
        Configures the group_by, column selection and text choices based on
        the resource name
        """
        if self.name == "ec2":
            return EC2_CONFIGURATION
        elif self.name == "s3":
            return S3_CONFIGURATION
        elif self.name == "rds":
            return RDS_CONFIGURATION
        elif self.name == "ebs":
            return EBS_CONFIGURATION

    def humanize_columns(self) -> pd.DataFrame:
        """
        Rename the columns to a human readable format.
        The human names of the colums are configured in the constants.py
        """
        humanized_columns = {
            **(self.configuration["column_mapping"]),
            **(self.configuration["recommendation_mapping"]),
            **(self.configuration["account_name_column_mapping"])
        }
        if self.name == "rds":
            humanized_columns.update(
                {**(self.configuration["storageRecommendation_mapping"])})

        return self.df.rename(
            columns=humanized_columns
        )

    def json_to_dataframe(self) -> pd.DataFrame:
        """
        Parse the raw json data from the API to a dataframe.
        Not all data from the API response is relevant.
        This method uses only the entries defined in the constants mapping.
        """
        cols = list(self.configuration["column_mapping"].keys())
        recommendation_cols = list(
            self.configuration["recommendation_mapping"].keys())
        account_name_cols = list(
            self.configuration["account_name_column_mapping"].keys())
        recommendation_grouping = list(
            self.configuration["recommendation_grouping"]["groupby"])
        # This line flattens out the recommendation object.
        df = pd.json_normalize(
            self.raw_data,
            record_path="recommendations",
            meta=cols,
            record_prefix="recommendations_",
            sep="_"
        )
        # Rds resources have two recommendation objects
        # So we must normalize both of the resources
        if self.name == "rds":
            storage_cols = list(
                self.configuration["storageRecommendation_mapping"].keys())
            df2 = pd.json_normalize(
                self.raw_data,
                record_path="storageRecommendations",
                meta=cols,
                record_prefix="storagerecommendations_",
                sep="_"
            )
            df = df.merge(df2, how="outer", on=cols)
            df = df.fillna({"storagerecommendations_action": "No Action"})
            recommendation_cols = (recommendation_cols + storage_cols)

        # Apply account id filtering.
        df = self.filter_account_ids(df)
        # Sort
        df["max"] = df.groupby(recommendation_grouping[0])[
            recommendation_grouping[1]].transform('max')
        df = df.sort_values(["max", recommendation_grouping[1]],
                            ascending=False).drop('max', axis=1)
        # Add account names to DF
        df = self.add_account_name(df)

        if df.empty:
            return df
        # Return the subselection based on column names inside the
        # configuration
        return self.order_columns(df[[*cols, *recommendation_cols, *account_name_cols]])

    def order_columns(self, df) -> pd.DataFrame:
        """
        Insert the accounts names column in the right spot.
        """
        account_name = df["vendorAccountName"]
        df = df.drop(columns=["vendorAccountName"])
        index_account_id = df.columns.get_loc("vendorAccountId")
        df.insert(loc=index_account_id,
                  column="vendorAccountName", value=account_name)
        return df

    def add_account_name(self, df) -> pd.DataFrame:
        """
        Add the account names to the main dataframe.
        It is necessary because account names come from a different
        API endpoint than the rest of the information.
        Returns the modified dataframe.
        """
        if df.empty:
            return df
        cols = list(self.configuration["account_name_mapping"].keys())
        df2 = pd.json_normalize(self.account_details, meta=cols, sep="_")
        df = df.merge(df2[cols], on="vendorAccountId")
        return df

    def filter_account_ids(self, df) -> pd.DataFrame:
        """Filter data based on the account ids passed on instantiation"""
        if len(self.account_ids) > 0:
            return df[df["vendorAccountId"].isin(self.account_ids)]
        return df

    def affected_accounts(self) -> pd.DataFrame:
        """Get the affected account names based on the recommendations"""
        terminate = self.recommendation_summary(action="terminate")
        rightsize = self.recommendation_summary(action="rightsize")
        affected_ids = pd.concat([
            terminate["vendorAccountId"], rightsize["vendorAccountId"]
        ], ignore_index=True)
        account_names = pd.DataFrame.from_records(
            self.account_details,
            columns=["vendorAccountName", "vendorAccountId"])

        # Filter the account names based on the actual recommendations
        return account_names[
            account_names["vendorAccountId"].isin(affected_ids)
        ]

    def get_best_recommendation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get best recommendations for a resource.
        Returns a dataframe with the columns described on the
        self.configuration attribute
        """
        grouping_meta = self.configuration["recommendation_grouping"]
        frames = []
        # Hacky way to get the best recommendations and preserve all the column
        # values without grouping
        for account in df["vendorAccountId"].unique():
            row_frame = df.loc[df["vendorAccountId"] == account].sort_values(
                # Sorting by vendorAccountId gives us fake grouping
                by=grouping_meta["groupby"],
                ascending=False
            ).head(1)[grouping_meta["selection"]]
            frames.append(row_frame)

        return pd.concat(frames)

    def count_recommendations(self, df) -> pd.DataFrame:
        """
        Count the total recommendations based on the
        action type: Rightsize or Terminate
        """
        return df.groupby(["vendorAccountId"]).size().reset_index(name="count")

    def build_recommendation(self, count_df, best_df) -> pd.DataFrame:
        """
        Merges both dataframes in order to get the dataframe that will be used
        to create the final recommendation messages.
        Works like an SQL left join
        """
        # The number of rows should be the same
        if (count_df.shape[0] != best_df.shape[0]):
            return None
        return count_df.merge(
            best_df,
            how="left",
            left_on="vendorAccountId",
            right_on="vendorAccountId"
        )

    def recommendation_summary(self, action="") -> pd.DataFrame:
        """
        Create the summary for the action (Rightsize or Terminate).
        This includes a recommendation count for each account id as well as
        a summarized message.
        """
        df = self.df.loc[self.df["recommendations_action"]
                         == action.capitalize()]
        if df.empty:
            return df
        count_df = self.count_recommendations(df)
        best_df = self.get_best_recommendation(df)
        return self.build_recommendation(count_df=count_df, best_df=best_df)
