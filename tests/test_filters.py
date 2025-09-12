import pytest
from datetime import datetime, timedelta
from journey_service.filters import filter_journeys

def test_filter_journeys_sorts_correctly():
    # Fake response
    now = datetime.now()
    result = {
        "data": {
            "planConnection": {
                "edges": [
                    {
                        "node": {
                            "start": (now + timedelta(minutes=10)).isoformat(),
                            "legs": [
                                {"to": {"name": "Stop A"}, "from": {"name": "Origin"}, "end": {"scheduledTime": (now + timedelta(minutes=30)).isoformat()}},
                            ],
                        }
                    },
                    {
                        "node": {
                            "start": (now + timedelta(minutes=5)).isoformat(),
                            "legs": [
                                {"to": {"name": "Stop B"}, "from": {"name": "Origin"}, "end": {"scheduledTime": (now + timedelta(minutes=20)).isoformat()}},
                            ],
                        }
                    },
                ]
            }
        }
    }

    journeys = filter_journeys(result)
    assert len(journeys) == 2
    # Check sorting by earliest start
    assert "Stop B" in journeys[0]
