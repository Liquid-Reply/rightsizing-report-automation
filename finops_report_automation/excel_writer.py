"""
Module that defines utility function to write excel files and formatting them
based on custom rules

This module works mainly by using pandas dataframes as input values and the
pandas.ExcelWriter

For more information:
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html

:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""
from datetime import date
import pandas as pd

from .resource import Resource
from .messages_helper import label
from .formatting import (
  format_color_groups,
  get_font,
  humanize_summary_columns,
  medium_border,
  color_terminate,
)


def write_summary_sheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    project_name: str,
    summary: pd.DataFrame,
    sum: pd.DataFrame
):
    """ Creates the general sheet for the project"""

    # Writes information about the report.
    current_row = 1
    pd.DataFrame().to_excel(writer, sheet_name, index=False, header=False)
    worksheet = writer.sheets[sheet_name]

    header_cell = worksheet.cell(
        row=current_row, column=1, value=f'Account overview for {project_name}')
    header_cell.font = get_font(size=16, color="black", bold=True)
    current_row += 1

    date_analysis_cell = worksheet.cell(
        row=current_row, column=1, value=f'State of analysis: {str(date.today())}')
    date_analysis_cell.font = get_font(size=9, color="black")
    current_row += 1

    review_period_cell = worksheet.cell(
        row=current_row, column=1, value=f'Review period: 10 days')
    review_period_cell.font = get_font(size=9, color="black")
    current_row += 1

    # Styling the report data.
    summary_len = len(summary)

    for col in ["highestOptimization", "monthlySavings", "annualSavings", "amortizedCost"]:
        summary[col] = summary[col].apply(lambda x: f"${x:.2f}")
    summary["relationPotentialSavings"] = summary["relationPotentialSavings"].apply(
        lambda x: f"{x:.2%}")

    summary_style = summary.style.applymap(
        lambda x: 'color:red;' if x == "Terminate" else 'color:black').apply(
            format_color_groups, group="name", axis=None).apply(
            color_terminate, axis=None)

    summary_style.to_excel(writer, sheet_name, startrow=current_row+1,
                           startcol=1, index=False, header=False)
    worksheet = writer.sheets[sheet_name]

    summary = humanize_summary_columns(summary)

    # We write the summary to column 'B'
    indentation = 2
    cells = worksheet[f'B{current_row+1}':f'K{current_row+1}']
    for cell in cells[0]:
        cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')
        cell.border = medium_border
        width_recommendation = len(
            str(summary.iloc[0, (cell.column - indentation)]))
        width_header = len(
            str(summary.columns[(cell.column - indentation)]))
        worksheet.column_dimensions[cell.column_letter].width = width_recommendation + 5 if width_recommendation > (
            width_header / 3) else (width_header / 3) + 5

    worksheet.row_dimensions[current_row+1].height = 55
    table_header = pd.DataFrame(list(summary.columns.values)).transpose()
    table_header = table_header.style.set_properties(
        **{'background-color': 'lightblue'})
    table_header.to_excel(writer, sheet_name, startrow=current_row,
                          startcol=1, index=False, header=False)

    current_row += summary_len + 2

    for col in ["monthly_saving_potential", "annual_savings_potential", "cost"]:
        sum[col] = sum[col].apply(lambda x: f"${x:.2f}")
    sum["relation"] = sum["relation"].apply(lambda x: f"{x:.2%}")

    sum.to_excel(writer, sheet_name, index=False, header=False,
                 startrow=current_row, startcol=6)
    sum_cell = worksheet.cell(
        row=current_row+1, column=2, value=f'SUM all accounts')
    sum_cell.font = get_font(size=12, color="black", bold=True)


def write_cross_project_sheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    summary: pd.DataFrame,
):
    """ Creates the cross-project overview excel file."""
    current_row = 1
    pd.DataFrame().to_excel(writer, sheet_name, index=False, header=False)
    worksheet = writer.sheets[sheet_name]

    header_cell = worksheet.cell(
        row=current_row, column=1, value="OVERVIEW: RECOMMENDATIONS ALL ACCOUNTS")
    header_cell.font = get_font(size=16, color="black", bold=True)
    current_row += 1

    summary.to_excel(writer, sheet_name, startrow=current_row+1,
                           startcol=0, index=False, header=False)
    worksheet = writer.sheets[sheet_name]

    summary = humanize_summary_columns(summary)
    summary = summary.rename(columns={"projectName": "Parent IT System"})


    indentation = 1
    cells = worksheet[f'A{current_row+1}':f'K{current_row+1}']
    for cell in cells[0]:
        cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')
        cell.border = medium_border
        # Format cell width based on the length of either the first value in the table or the header, depending of which is longer.
        width_recommendation = len(
            str(summary.iloc[0, (cell.column - indentation)]))
        width_header = len(
            str(summary.columns[(cell.column - indentation)]))
        worksheet.column_dimensions[cell.column_letter].width = width_recommendation + 5 if width_recommendation > (
            width_header / 3) else (width_header / 3) + 5

    worksheet.row_dimensions[current_row+1].height = 55
    table_header = pd.DataFrame(list(summary.columns.values)).transpose()
    table_header = table_header.style.set_properties(
        **{'background-color': 'lightblue'})
    table_header.to_excel(writer, sheet_name, startrow=current_row,
                          startcol=0, index=False, header=False)

def write_resource_sheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    resource: Resource
):
    """Creates the excel report for the specified resource"""
    # Dataframes to be dumped into excel
    accounts = resource.affected_accounts()
    rightsize = resource.recommendation_summary(action="rightsize")
    terminate = resource.recommendation_summary(action="terminate")

    current_row = 1

    # There is a bug that happens when a workbook is newly created without
    # visible sheets and is attempted to write a simple text into it. The sheet
    # will not be created automatically by writing a simple test. Therefore a
    # dataframe shall be writed first in order to create the sheet

    # The df.to_excel function is 0-indexed!
    accounts.to_excel(writer, sheet_name, startrow=current_row,
                      header=False, index=False)
    worksheet = writer.sheets[sheet_name]

    for row in range(len(accounts)):
        cells = worksheet[current_row + row + 1]
        for cell in cells[0:len(cells)]:
            cell.border = medium_border

    # The cell function is 1-indexed!
    acc_cell = worksheet.cell(
        row=current_row, column=1, value="Accounts Affected")
    acc_cell.font = get_font(size=14, color="blue", bold=True)

    current_row += 3 + len(accounts)

    rec_cell = worksheet.cell(
        row=current_row, column=1, value="Recommendations")
    rec_cell.font = get_font(size=14, color="blue", bold=True)

    current_row += 1

    # Write the termination section of the recommendations

    term_cell = worksheet.cell(row=current_row, column=1, value="Termination")
    term_cell.font = get_font(size=11, color="red", bold=True)

    message_terminate = label(resource, terminate, "terminate")
    message_terminate.to_excel(
        writer, sheet_name, startrow=current_row, header=False, index=False)
    current_row += 2 + len(terminate)

    # Write the rightsizing section of the recommendations
    right_cell = worksheet.cell(row=current_row, column=1, value="Rightsizing")
    right_cell.font = get_font(size=11, color="black", bold=True)

    message_rightsize = label(resource, rightsize, "rightsize")
    message_rightsize.to_excel(
        writer, sheet_name, startrow=current_row, header=False, index=False)
    current_row += 4 + len(rightsize)

    # Write the based reporting section
    based_cell = worksheet.cell(
        row=current_row, column=1, value="Based Reporting")
    based_cell.font = get_font(size=14, color="blue", bold=True)
    current_row += 1

    # First info message
    info_message = "Please find all utilization analysis per resource in Cloudability -> Rightsizing -> EC2."
    info_cell = worksheet.cell(row=current_row, column=1, value=info_message)
    info_cell.font = get_font(size=10, color="light_purple")
    current_row += 1

    # Second info message
    info_message = "! Considered basis: Effective Costs. Recommendations take into account historical reservation coverage for the current instance."
    info_cell = worksheet.cell(row=current_row, column=1, value=info_message)
    info_cell.font = get_font(size=10, color="pink")
    current_row += 1

    # Write the consolidate report to the excel
    resource_df = resource.df.style.apply(format_color_groups, group="vendorAccountId", axis=None).applymap(
        lambda x: 'color:red;' if x == "Terminate" else 'color:black')
    resource_df.to_excel(writer, sheet_name,
                         startrow=current_row, index=False, header=False)

    resource.df = resource.humanize_columns()
    worksheet.row_dimensions[current_row].height = 55
    table_header = pd.DataFrame(list(resource.df.columns.values)).transpose()
    table_header = table_header.style.set_properties(
        **{'background-color': 'lightblue'})
    table_header.to_excel(writer, sheet_name, startrow=current_row - 1,
                          index=False, header=False)

    cells = worksheet[current_row]
    for cell in cells[0:len(cells)]:
        cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')
        cell.border = medium_border
        width_recommendation = len(str(resource.df.iloc[0, (cell.column - 1)]))
        width_header = len(str(resource.df.columns[(cell.column - 1)]))
        worksheet.column_dimensions[cell.column_letter].width = width_recommendation + 5 if width_recommendation > (
            width_header / 3) else (width_header / 3) + 5
