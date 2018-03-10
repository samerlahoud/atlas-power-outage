#!/root/anaconda3/bin/python
import json
import requests
from ripe.atlas.cousteau import ProbeRequest
from collections import defaultdict
import time

def get_probes(cc):
    filters = {}
    filters['country_code'] = cc
    probes = ProbeRequest(**filters)
    probe_id = {p["id"] for p in probes}
    return probe_id

def get_events(cc, start_timestamp, end_timestamp):
    disco_event=defaultdict(list)
    conn_event=defaultdict(list)
    latest_disco=defaultdict(list)
    disco_time=defaultdict(list)
    
    probe_id = get_probes(cc)
    for probe in probe_id:
        latest_disco[probe] = 0

    api_url = "https://atlas.ripe.net/api/v2/measurements/7000/results?start={}&end={}&format=json".format(start_timestamp,end_timestamp)
    response = requests.get(api_url)
    
    if response.status_code == 200:
        event_json = json.loads(response.content.decode('utf-8'))
        for item in event_json:
            if (item['prb_id'] in probe_id):
                if(item['event'] == 'connect'):
                    conn_event[item['prb_id']].append(item['timestamp'])
                    if(latest_disco[item['prb_id']]):
                        disco_time[item['prb_id']].append(int(item['timestamp'])-int(latest_disco[item['prb_id']]))
                else:
                    disco_event[item['prb_id']].append(item['timestamp'])
                    latest_disco[item['prb_id']] = item['timestamp']
        return(conn_event,disco_event,disco_time)
    else:
        return None

def analyze_events(conn_event,disco_event,disco_time):
    #sorted_event=defaultdict(list)
    #for probe_id in disco_event:
    #    if min(conn_event[probe_id]) < min(disco_event[probe_id]):
    #        disco_event[probe_id].append(start_timestamp)    
    #    sorted_event[probe_id] = sorted(disco_event[probe_id] + conn_event[probe_id])
    #for probe_id on sorted_event:
        
    print(conn_event,disco_event,disco_time)
             

if __name__ == "__main__":
    start_time = '1520623355'
    end_time = time.time()
    cc = 'LB'

    conn_event, disco_event, disco_time = get_events(cc,start_time,end_time)
    analyze_events(conn_event,disco_event,disco_time)

