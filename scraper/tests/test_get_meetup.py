import core
import json

def test_ics_to_dict():
    with open("tests/data/bourbonfriday.ics") as fp:
        data = fp.read().strip()
    name, list = core.parse_ics(data)
    assert name == "Bourbon Friday"
    assert list


def test_parse_html():
    with open("tests/data/test_event.html") as fp:
        data = fp.read().strip()
    
    result = core.pull_json_from_html(data)
    assert type(result) is dict

def test_get_event_data_from_raw_json_from_event_url():
    with open("tests/data/event_data.json") as fp:
        data = json.load(fp)

    result = core.get_event_data_from_raw_json_from_event_url(data)
    
    assert "venue" in result
    assert "going" in result
    assert "title" in result
    assert "description" in result
    assert "eventPhoto" in result
    assert "eventHost" in result
    assert "eventHostPhoto" in result
    assert "start" in result
    assert "end" in result
    assert "url" in result

def test_get_event_data_from_raw_json_from_event_url_pystl():
    with open("tests/data/pystl_event_data.json") as fp:
        data = json.load(fp)

    result = core.get_event_data_from_raw_json_from_event_url(data)