"""
:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""

import os
import yaml
from datetime import date
import boto3
import logging
from .logger import create_logger
from .aws import upload_to_s3
from .api import Api
from .project import create_cross_project_overview, create_projects
from .utils import write_file, use_offline_data


USE_LOCAL_DATA = os.environ.get("USE_LOCAL_DATA") or False
DEBUG = os.environ.get("DEBUG") or False
REPORTINGS_PATH = os.environ.get("REPORTINGS_PATH", "./reports")
PROJECT_NAMES_FILE = f"{os.environ.get('CONFIG_PATH', './config')}/accountMapping.xlsx"
CONFIG_PATH = os.environ.get("CONFIG_PATH") or "./config"
USE_OFFLINE_MODE = True
BUCKET_NAME = os.environ.get("BUCKET_NAME") or False

logger = create_logger()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    logger.debug("Using debug mode.")


def main():

    s3_client = boto3.client("s3")
    api = Api("https://api.cloudability.com")

    if USE_LOCAL_DATA:
        account_details = use_offline_data("./config/accounts.json")
    else:
        account_details = api.get_accounts()

    amortized_cost_raw = api.get_amortized_cost()
    projects = create_projects(amortized_cost_raw)

    date_str = str(date.today()).replace("-", "/")
    config_list = []
    with open(f"{CONFIG_PATH}/config.yaml", "r") as config_file:
        config_iterator = yaml.load_all(config_file, Loader=yaml.FullLoader)
        for c in config_iterator:
            config_list.append(c)

    for config in config_list:
        logger.debug(f"Handling {config['product']} data.")
        if USE_LOCAL_DATA:
            api_data = use_offline_data(
                f"{REPORTINGS_PATH}/output_{config['product']}.json")
        else:
            api_data = api.get_rightsizing(config)
            filepath_api = write_file(f"{REPORTINGS_PATH}/{config['product']}_api.json", str(api_data))
            if BUCKET_NAME != False:
                logger.info(f"Uploading {config['product']}_api.json to S3")
                upload_to_s3(s3_client, filepath_api, f"{date_str}/raw_api/{config['product']}_api.json")
            for project in projects:
                logger.debug(f"Appending {config['product']} to {project}")
                project.append_resource(
                    config["product"],
                    api_data["result"],
                    project.account_ids,
                    account_details["result"]
                    )

    # Final report writing
    dataframes_list = []
    for project in projects:
        if len(project.resources) > 0:
            dataframes_list.append(project.summary)
        filepath_projects = project.write_report(f"{REPORTINGS_PATH}")
        if len(filepath_projects) > 0 and BUCKET_NAME != False:
            logger.info(f"Uploading {project.name}.xlsx to S3")
            upload_to_s3(s3_client, filepath_projects, f"{date_str}/Project reports/{project.name}.xlsx")
        
    filepath_summary = create_cross_project_overview(dataframes_list)
    filepath_amortized_cost = write_file(f"{REPORTINGS_PATH}/amortized_cost_api.json", str(amortized_cost_raw))
    if BUCKET_NAME != False:
        logger.info(f"Uploading amortized_cost_api.json to S3")
        upload_to_s3(s3_client, filepath_amortized_cost, f"{date_str}/raw_api/amortized_cost_api.json")
        logger.info(f"Uploading cross_project_overview.xlsx to S3")
        upload_to_s3(s3_client, filepath_summary, f"{date_str}/cross_project_overview.xlsx")

    logger.info("Finished creating & uploading reports.")

if __name__ == "__main__":
    main()
