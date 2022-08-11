"""
Module that holds all the utility functions needed to modify
cell formatting by directly modifying the cells with openpyxl
or using the Dataframes.io.style properties

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""
import pandas as pd
from openpyxl.styles import Font
from .errors import ColorError
from .constants import GENERAL_SHEET_CONFIGURATION
from openpyxl.styles.borders import Border, Side

FONT_FAMILY = "Heebo"
COLORS = {
    "blue": "4f71be",
    "red": "ea3423",
    "pink": "eb48c8",
    "black": "000000",
    "light_purple": "8c5371"
}

medium_border = Border(left=Side(style='medium'),
                       right=Side(style='medium'),
                       top=Side(style='medium'),
                       bottom=Side(style='medium'))


def color_terminate(df):
    """
    Change the background color of rows containing a terminate recommendation
    to red.
    """
    x = df.copy()
    x.loc[x['recommendations_action'] == "Terminate",
          :] = 'background-color: #FFE0DF'
    x.loc[x['recommendations_action'] == "Rightsize",
          :] = None
    return x


def format_color_groups(df, group):
    """
    Change the background color of related recommendations
    alternatingly white and grey for readability reasons.
    Returns a pandas Styler.
    """
    colors = ['white', '#ebebeb']
    x = df.copy()
    grouping_meta = list(x[group].unique())
    i = 0
    for group_item in grouping_meta:
        style = f'background-color: {colors[i]}'
        x.loc[x[group] == group_item, :] = style
        i = not i
    return x


def humanize_summary_columns(df) -> pd.DataFrame:
    """
    Rename columns to a human readable format
    """
    humanized_columns = {
        **(GENERAL_SHEET_CONFIGURATION["column_mapping"]),
    }
    return df.rename(
        columns=humanized_columns
    )


def get_font(size: int = 10, color: str = "", bold=False):
    """Return the font class used to style text"""
    if color not in COLORS.keys():
        raise ColorError("Color not available!")
    return Font(name=FONT_FAMILY,
                size=size,
                bold=bold,
                color=COLORS[color])
