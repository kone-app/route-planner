from datetime import datetime
from .utils import format_arrival_time

def filter_journeys(result):
    journeys = []
    edges = result["data"]["planConnection"]["edges"]
    sorted_edges = sorted(edges, key=lambda e: datetime.fromisoformat(e["node"]["start"]))

    for i in sorted_edges:
        start_location = i['node']['legs'][0]['to']['name']
        end = i['node']['legs'][-1]
        end_location = end['from']['name']
        arrival_time = format_arrival_time(end['end']['scheduledTime'])
        journeys.append(f"{arrival_time}, {start_location}, {end_location}")

    return journeys
