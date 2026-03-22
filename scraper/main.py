import logging
import datetime
import boto3
import os
import json
import core
import requests
from datetime import datetime, timezone, timedelta

central = timezone(timedelta(hours=-6), name="CST")


# Create a logger
logging.basicConfig(
    level=logging.INFO,      # set to DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def main():
    s3 = boto3.Session(profile_name=os.environ.get("AWS_PROFILE")).client("s3")
    bucket_name = "stlcodecal"
    object_key = "meetups.json"
        
    try:
        # Get the object
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read the body and decode to string
        json_content = response['Body'].read().decode('utf-8')

        # Parse JSON into a Python dictionary
        data = json.loads(json_content)
        
    except Exception as e:
        logger.error("Error reading file:", e)
    
    now = datetime.now(central)
    pretty_now = now.strftime("%m/%d/%Y %I:%M %p")
    filename_now = now.strftime("%Y%m%d_%H%M%S")
    export = {
        "lastUpdated": now.isoformat(),
        "lastUpdatedPretty": pretty_now,
        "events": {

        }
    }

    events_data = export["events"]
    for meetup_url in data:
        try:
            result = requests.get(f"{meetup_url}/events/ical")
            calendar_text = result.text
        except Exception as e:
            logger.error(f"Failed to pull data from {meetup_url}")
            continue
            
        name, events = core.parse_ics(calendar_text)
        list = events_data[name] = []

        try:
            for event in events:
                if event["status"] != "CONFIRMED":
                    continue
                
                event_data = core.pull_event_from_url(event["url"])
                logger.info(f"Successfully pulled event from {event['url']}")
                relevant_info = core.get_event_data_from_raw_json_from_event_url(event_data)
                logger.info(f"Successfully parsed event")
                list.append(relevant_info)         
        except Exception as e:
            logger.error(f"Failed to process event: {name}: {e}")
    

    event_object_name = f"events_{filename_now}.json"
    event_latest_tag = f"events_latest.json"
            
    try:
        # Convert dict to JSON string and upload
        s3.put_object(
            Bucket=bucket_name,
            Key=event_object_name,
            Body=json.dumps(export, indent=2),  # pretty-print with indent
            ContentType="application/json"
        )
        logger.info(f"Uploaded {event_object_name} to bucket {bucket_name}")
        
        s3.put_object(
            Bucket=bucket_name,
            Key=event_latest_tag,
            Body=json.dumps(export, indent=2),  # pretty-print with indent
            ContentType="application/json"
        )
        logger.info(f"Uploaded {event_latest_tag} to bucket {bucket_name}")


    except Exception as e:
        logger.error(f"Error uploading JSON: {e}")

if __name__ == "__main__":
    main()