#!/root/anaconda3/bin/python
import json
import requests
import time
import sys
from ripe.atlas.cousteau import ProbeRequest
from collections import defaultdict
from bisect import bisect_right
from datetime import datetime
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
    disco_duration=defaultdict(list)
    for probe_id in conn_event:
        for conn_time in conn_event[probe_id]:
            # Locate the the lowest nearest disconnection
            nearest_disco = bisect_right(disco_event[probe_id], conn_time)
            if nearest_disco == 0:
                nearest_disco_time = int(start_time)
            else:
                nearest_disco_time = int(disco_event[probe_id][nearest_disco-1])
            disco_duration[probe_id].append(int(conn_time)-nearest_disco_time)
    return(disco_duration)

def plot_disco_duration(disco_duration,cc):
    merge_disco_duration = []
    for d in disco_duration.values():
        merge_disco_duration = merge_disco_duration + d
    fig, ax = plt.subplots()
    ax.violinplot(np.log10(merge_disco_duration), showmedians=True)
    #ax.set_yscale("log", nonposy='clip')
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_xticklabels([])
    plt.ylabel('log10(Disconnection duration in seconds)')
    fig.savefig('disco_duration_dist_{}.png'.format(cc))
    plt.close(fig)

def plot_disco_time(disco_event):
    merge_disco_time=[]
    merge_disco_hour=[]
    for d in disco_event.values():
        merge_disco_time = merge_disco_time + d
        for e in d: 
            merge_disco_hour.append(datetime.fromtimestamp(e).hour)
    fig, ax = plt.subplots()
    merge_disco_hour = np.array(merge_disco_hour)
    ax.hist(merge_disco_hour, bins=np.arange(merge_disco_hour.min(), merge_disco_hour.max()+1))
    #ax.set_yscale("log", nonposy='clip')
    ax.grid(True)
    plt.ylabel('Disconnection time')
    fig.savefig('disco_time_dist_{}.png'.format(cc))
    plt.close(fig)

if __name__ == "__main__":
    cc = str(sys.argv[1])
    #start_time = '1520630104'
    start_time = '1523905107'
    end_time = time.time()
    conn_event, disco_event = get_events(cc,start_time,end_time)
    conn_event_json = json.dumps(conn_event)
    disco_event_json = json.dumps(disco_event)
    disco_duration = analyze_events(conn_event,disco_event,start_time)
    disco_duration_json = json.dumps(disco_duration)

    plot_disco_duration(disco_duration,cc)
    plot_disco_time(disco_event)

    f = open("conn_event_{}_{}_{}.json".format(cc,start_time,end_time),"w")
    f.write(conn_event_json)
    f.close()
    f = open("disco_event_{}_{}_{}.json".format(cc,start_time,end_time),"w")
    f.write(disco_event_json)
    f.close()
    f = open("disco_duration_{}_{}_{}.json".format(cc,start_time,end_time),"w")
    f.write(disco_duration_json)
    f.close()
    
