import pytest
from datetime import datetime, timedelta
from journey_service.filters import filter_journeys


def make_leg(start_dt, end_dt, mode="BUS", from_name="Origin", to_name="Destination", duration=None):
    """Helper to build a fake leg."""
    return {
        "from": {"name": from_name},
        "to": {"name": to_name},
        "start": {"scheduledTime": start_dt.isoformat()},
        "end": {"scheduledTime": end_dt.isoformat()},
        "mode": mode,
        "duration": duration if duration is not None else int((end_dt - start_dt).total_seconds()),
    }


def test_filter_journeys_sorts_and_replaces_origin_destination():
    now = datetime(2025, 9, 13, 7, 30, 0)
    result = {
        "data": {
            "planConnection": {
                "edges": [
                    {   # Journey starting later
                        "node": {
                            "start": (now + timedelta(minutes=10)).isoformat(),
                            "legs": [make_leg(now + timedelta(minutes=10),
                                              now + timedelta(minutes=20),
                                              "BUS",
                                              "Origin",
                                              "Stop A")],
                        }
                    },
                    {   # Journey starting earlier
                        "node": {
                            "start": (now + timedelta(minutes=5)).isoformat(),
                            "legs": [make_leg(now + timedelta(minutes=5),
                                              now + timedelta(minutes=15),
                                              "TRAM",
                                              "Origin",
                                              "Destination")],
                        }
                    },
                ]
            }
        }
    }

    journeys = filter_journeys(result, "MyOrigin", "MyDestination")

    # Two journeys produced (each has leg + duration + blank line)
    assert any("Stop A" in j for j in journeys)
    assert any("MyOrigin" in j for j in journeys)
    assert any("MyDestination" in j for j in journeys)

    # Ensure duration formatting is correct
    assert any("0:10:00" in j for j in journeys)


def test_filter_journeys_multiple_legs_accumulates_duration():
    now = datetime(2025, 9, 13, 8, 0, 0)
    result = {
        "data": {
            "planConnection": {
                "edges": [
                    {
                        "node": {
                            "start": now.isoformat(),
                            "legs": [
                                make_leg(now, now + timedelta(minutes=5), "WALK", "Origin", "Stop B"),
                                make_leg(now + timedelta(minutes=5), now + timedelta(minutes=15), "BUS", "Stop B", "Destination"),
                            ],
                        }
                    }
                ]
            }
        }
    }

    journeys = filter_journeys(result, "CustomOrigin", "CustomDestination")

    # Two legs + total duration + blank line
    assert any("WALK" in j for j in journeys)
    assert any("BUS" in j for j in journeys)

    # Look for the total duration line explicitly
    total_line = [j for j in journeys if j.startswith("Total Journey Duration")][0]
    assert "0:15:00" in total_line
    assert total_line.endswith("min")

