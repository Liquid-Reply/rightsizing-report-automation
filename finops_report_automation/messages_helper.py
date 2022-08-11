"""
Module that holds helper functions used for templating the
recommendation messages in a human readable form

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

from .resource import Resource
import pandas as pd


def label(resource: Resource, df: pd.DataFrame, action) -> pd.DataFrame:
    """
    Convert the recommendation dataframe with multiple columns to a single column in human readable form.
    This function is for EC2, EBS and S3 resources.
    Returns a dataframe.
    """
    if resource.name == "rds":
        return label_rds(resource, df, action)
    templates = resource.configuration["messages"][action]
    if df.empty:
        return pd.DataFrame({"message": [templates['zero']]})
    for i, row in df.iterrows():
        row_dict = row.to_dict()
        if row['count'] == 1:
            message = templates["one"].format(**row_dict)
        elif row['count'] > 1:
            message = templates["moreThanOne"].format(**row_dict)
        df.at[i, 'message'] = message
    return pd.DataFrame(df['message'])


def label_rds(resource: Resource, df: pd.DataFrame, action) -> pd.DataFrame:
    """
    Convert the recommendation dataframe with multiple columns to a single column in human readable form.
    This function is for RDS resources.
    Returns a dataframe.    
    """
    templates = resource.configuration["messages"][action]
    template_message = resource.configuration["messages"]["storage_message"]
    if df.empty:
        return pd.DataFrame({"message": [templates['zero']]})
    for i, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict["storage"] = template_message[row_dict["storagerecommendations_action"].lower(
        ).replace(" ", "")]
        if row['count'] == 1:
            message = templates["one"].format(**row_dict)
        elif row['count'] > 1:
            message = templates["moreThanOne"].format(**row_dict)

        df.at[i, 'message'] = message
    return pd.DataFrame(df['message'])
