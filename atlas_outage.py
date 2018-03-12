#!/root/anaconda3/bin/python
import json
import requests
import time
from ripe.atlas.cousteau import ProbeRequest
from collections import defaultdict
from bisect import bisect_right
import matplotlib.pyplot as plt
import numpy as np

def get_probes(cc):
    filters = {}
    filters['country_code'] = cc
    probes = ProbeRequest(**filters)
    probe_id = {p["id"] for p in probes}
    return probe_id

def get_events(cc, start_timestamp, end_timestamp):
    disco_event=defaultdict(list)
    conn_event=defaultdict(list)
    
    probe_id = get_probes(cc)
    #probe_id = [34212]

    api_url = "https://atlas.ripe.net/api/v2/measurements/7000/results?start={}&end={}&format=json"\
                .format(start_timestamp,end_timestamp)
    response = requests.get(api_url)
    
    if response.status_code == 200:
        event_json = json.loads(response.content.decode('utf-8'))
        for item in event_json:
            if (item['prb_id'] in probe_id):
                if(item['event'] == 'connect'):
                    conn_event[item['prb_id']].append(item['timestamp'])
                else:
                    disco_event[item['prb_id']].append(item['timestamp'])
        return(conn_event,disco_event)
    else:
        return None

def analyze_events(conn_event,disco_event,start_time):
    disco_time=defaultdict(list)
    for probe_id in conn_event:
        for conn_time in conn_event[probe_id]:
            # Locate the the lowest nearest disconnection
            nearest_disco = bisect_right(disco_event[probe_id], conn_time)
            if nearest_disco == 0:
                nearest_disco_time = int(start_time)
            else:
                nearest_disco_time = int(disco_event[probe_id][nearest_disco-1])
            disco_time[probe_id].append(int(conn_time)-nearest_disco_time)
    return(disco_time)

def plot_disco_time(disco_time):
    merge_disco_time = []
    for d in disco_time.values():
        merge_disco_time = merge_disco_time + d
    fig, ax = plt.subplots()
    ax.violinplot(np.log10(merge_disco_time), showmedians=True)
    #ax.set_yscale("log", nonposy='clip')
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_xticklabels([])
    plt.ylabel('log10(Disconnection time in seconds)')
    fig.savefig('disco_time_dist.png')
    plt.close(fig)

if __name__ == "__main__":
    #start_time = '1520623355'
    start_time = '1518363868'
    end_time = time.time()
    cc = 'LB'
    #cc = 'NL'
    conn_event, disco_event = get_events(cc,start_time,end_time)
    disco_time = analyze_events(conn_event,disco_event,start_time)
    plot_disco_time(disco_time)
    print(disco_time)

