import requests
import logging
import json
import os,sys
import functions_framework
from datetime import datetime
from bibt.gcp import bq
from bibt.gcp import pubsub
from bibt.gcp import secrets
from bibt.gcp import storage

if os.environ.get("FUNCTION_NAME") or os.environ.get("K_SERVICE"):
    # if os.environ.get("GAE_APPLICATION"):
    from google.cloud import logging as glogging

    client = glogging.Client()

    log_level = (
        logging.INFO if os.environ.get("_DEPLOY_ENV") == "prod" else logging.DEBUG
    )

    client.setup_logging(log_level=log_level, excluded_loggers=("urllib3", "google"))
else:
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout,
        # filename="out.log",
        format=(
            "[%(asctime)s] "
            # '%(name)s | ' # logger name
            "%(levelname)s "
            "<%(module)s:%(funcName)s:%(lineno)s>:  "
            "%(message)s"
        ),
        force=True,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


#API Call to fetch EOL info of Operations Systems

def get_eol_data(os):
    url = f"https://endoflife.date/api/{os}.json"
    logging.info(f"Fetching data from URL: {url}")

    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()

    data = response.json()
    logging.info("Data fetched successfully")

    parsed_data = []

    if os == "macos":
        for item in data[:4]:
            parsed_item = {
                "os_version": item["cycle"],
                "os_release": item["latest"],
                "EOL": bool(item["eol"]),
                "EOL_DATE": item["eol"] if isinstance(item["eol"], str) else None
            }
            parsed_data.append(parsed_item)
        logging.info("Parsed macOS data")
    elif os == "windows":
        for item in data:
            parsed_item = {
                "os_version": item["cycle"],
                "os_release": item["releaseDate"],
                "EOL_DATE": item["eol"]
            }
            parsed_data.append(parsed_item)
        logging.info("Parsed Windows data")
    elif os in ["linux", "ubuntu", "rhel", "centos"]:
        for item in data:
            parsed_item = {
                "os_version": item["cycle"],
                "os_release": item["latest"],
                "EOL": item["eol"],
            }
            parsed_data.append(parsed_item)
        logging.info(f"Parsed {os} data")

    return (parsed_data)


#Function to Upload json data to GCS Bucket
def upload(eol_data):
    logging.info("Starting upload to Google Cloud Storage")
    
    gcs_client = storage.Client(project_id="terraform-karthik-test")
    gcs_client.write_gcs_nldjson(
        bucket_name="aim-test-1-salman",
        blob_name="test-1",
        json_data=eol_data
    )
    logging.info("Upload completed")
    
    try:
        logging.info("Initializing BigQuery client.")
        bq_client = bq.Client(project_id="terraform-karthik-test")

        logging.info("Loading schema from schema.json.")
        with open("schema.json", "r") as infile:
            schema = json.load(infile)

        logging.info("Uploading data to BigQuery.")
        bq_client.upload_gcs_json(
            bucket_name="aim-test-1-salman",
            blob_name="test-1",
            bq_project="terraform-karthik-test",
            dataset="aim_test_salman",
            table="aim_test_macOS",
            schema_json_path="schema.json",
            ignore_unknown=True,
            append=True,
        )
        logging.info("Data upload to BigQuery completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise
    
#Main Entrypoint for CF
@functions_framework.http
def main(req):
    os = "macos"
    #for os in os_list:
    logging.info(f"Processing OS: {os}")
    eol_data = get_eol_data(os)
    print("---->")
    print(eol_data)
    logging.info(f"EOL data for {os}: {eol_data}")
    upload(eol_data)
    logging.info(f"Completed processing for {os}")
    return "Completed"