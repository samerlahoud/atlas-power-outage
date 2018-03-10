#!/root/anaconda3/bin/python
import json
import requests
from ripe.atlas.cousteau import ProbeRequest

api_url = "https://atlas.ripe.net/api/v2/measurements/7000/results?start=1519900968&format=json"
response = requests.get(api_url)

def get_probes(cc):
    #filters = {"country_code": {}}.format(cc)
    filters = {}
    filters['country_code'] = cc
    probes = ProbeRequest(**filters)
    probe_ids = {probe["id"] for probe in probes}
    return probe_ids

def get_events(cc):
    probe_ids = get_probes(cc)
    if response.status_code == 200:
        event_json = json.loads(response.content.decode('utf-8'))
        for item in event_json:
            if item['prb_id'] in probe_ids:
                print(item)
        return 1
    else:
        return None

if __name__ == "__main__":
    get_events("LB")
