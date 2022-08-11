"""
:license: AGPL v3, see LICENSE for more details
:copyright: 2022 Liquid Reply GmbH
"""
import os
import logging


BUCKET_NAME = os.environ.get("BUCKET_NAME") or False

logging.getLogger()

def upload_to_s3(s3_client, local_file, file_with_path): 
    """
    Upload files to S3. file_with_path should include the full path to where the file should be stored.
    E.g. 2022/05/12/cross_project_overview.xlsx
    """
    try:
        s3_client.upload_file(local_file, f"{BUCKET_NAME}", file_with_path )
    except FileNotFoundError:
        logging.info("The file was not found")
        return ""    
    except KeyError:
        return ""



# Placeholder for a SQS integration

# notify 