import requests
from datetime import datetime
from .config import API_KEY,GEO_CODING_URL,ROUTING_URL

def get_coordinates(origin, destination):
    url = GEO_CODING_URL
    headers = {"Accept": "application/json", "digitransit-subscription-key": API_KEY}

    origin_response = requests.get(url, headers=headers, params={"text": origin}).json()
    destination_response = requests.get(url, headers=headers, params={"text": destination}).json()

    origin_coordinates = origin_response['features'][0]['geometry']['coordinates']
    destination_coordinates = destination_response['features'][0]['geometry']['coordinates']

    return origin_coordinates, destination_coordinates


def query_journeys(origin_coordinates, destination_coordinates, arriveBy):
    origin = f"origin: {{ location: {{ coordinate: {{ latitude: {origin_coordinates[1]}, longitude: {origin_coordinates[0]} }} }} }}"
    destination = f"destination: {{ location: {{ coordinate: {{ latitude: {destination_coordinates[1]}, longitude: {destination_coordinates[0]} }} }} }}"
    latestArrival = '"' + datetime.strptime(arriveBy, "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S+03:00") + '"'

    query = """
    {
        planConnection("""+ origin + destination +"""    first: 10
            dateTime:  {
            latestArrival: """ + latestArrival + """
            }
        ) {
        edges {
            node {
                start
                end
                legs {
                    from {
                        name
                    }
                    to {
                        name
                    }
                    start {
                        scheduledTime
                    }
                    end {
                        scheduledTime
                        }
                    mode
                    duration
                    realtimeState
                    }
                }
            }
        }
    }"""


    routing_url = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
    #routing_url = ROUTING_URL
    response = requests.post(
        url=routing_url,
        headers={"Content-Type": "application/json", "digitransit-subscription-key": API_KEY},
        json={"query": query}
    )
    response.raise_for_status()
    return response.json()
