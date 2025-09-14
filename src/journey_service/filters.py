from datetime import datetime, timedelta
from .utils import format_arrival_time

def filter_journeys(result, origin, destination):
    journeys = []
    edges = result["data"]["planConnection"]["edges"]
    sorted_edges = sorted(edges, key=lambda e: datetime.fromisoformat(e["node"]["start"]))[-10:]
    journeys.append("Route Details :-")
    for i in sorted_edges:
        journey_duration = 0
        for j in i['node']['legs']:
            start_time = datetime.fromisoformat(j['start']['scheduledTime'].split("+")[0]).strftime("%H:%M:%S")
            end_time = datetime.fromisoformat(j['end']['scheduledTime'].split("+")[0]).strftime("%H:%M:%S")
            duration = j['duration']
            from_loc = j['from']['name']
            if from_loc == "Origin":
                from_loc = origin
            to_loc = j['to']['name']
            if to_loc == "Destination":
                to_loc = destination
            journeys.append("Time to leave from " + from_loc + " : " + start_time)
            journey = from_loc + ":"+start_time + "  --TO-->  " + to_loc + ":"+end_time + "  BY-->  " + j['mode'] + " " + str(timedelta(seconds=duration))+" min"
            journeys.append(journey)
            journey_duration += duration
        journeys.append("Total Journey Duration = " + str(timedelta(seconds=journey_duration))+" min")
        journeys.append("")
        journeys.append("")
    return journeys
