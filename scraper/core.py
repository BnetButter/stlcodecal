import sys
import os
import json
import re
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), "packages"))

import requests
from ics import Calendar

def parse_ics(ics_text) -> tuple[str, list]:
    match = re.search(r"X-WR-CALNAME:(.+)", ics_text)
    calendar_name = match.group(1).strip() if match else None
    events = []
    cal = Calendar(ics_text)
    for event in cal.events:
        data = {
            "id": event.uid,
            "summary": event.name,
            "start": str(event.begin),
            "end": str(event.end),
            "description": event.description,
            "url": event.url,
            "status": event.status,
            "created": str(event.created),
            "last_modified": str(event.last_modified),
        }
        events.append(data)
    return calendar_name, events




def pull_json_from_html(html) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Find <script> tag with type="application/json"
    script_tag = soup.find("script", type="application/json")

    if script_tag:
        # Get inner text
        json_text = script_tag.string.strip()
        
        # Convert to Python dict
        data = json.loads(json_text)

    return data



def pull_event_from_url(url) -> dict:
    data = requests.get(url)
    html = data.text
    return pull_json_from_html(html)


def get_event_data_from_raw_json_from_event_url(data: dict) -> dict:
    event = data["props"]["pageProps"]["event"]

    eventHosts = event["eventHosts"]
    eventHost = None
    eventHostPhoto = None
    if eventHosts:
        eventHost =  event["eventHosts"][0]["name"]
        try:
            eventHostPhoto = event["eventHosts"][0]["memberPhoto"]["baseUrl"] + event["eventHosts"][0]["memberPhoto"]["id"],
        except:
            pass
    

    return {
        "venue": event.get("venue"),
        "going": event["goingCount"]["totalCount"],
        "title": event["title"],
        "description": event["description"],
        "eventPhoto": event["featuredEventPhoto"]["source"] if event["featuredEventPhoto"] else None,
        "eventHost": eventHost,
        "eventHostPhoto": eventHostPhoto,
        "start": event["dateTime"],
        "end": event["endTime"],
        "url": event["eventUrl"],
    }

