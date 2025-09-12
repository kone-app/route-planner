import pytest
import requests
from unittest.mock import patch, MagicMock
from journey_service import digitransit

@patch("journey_service.digitransit.requests.get")
def test_get_coordinates_success(mock_get):
    # mock origin
    mock_origin = {"features": [{"geometry": {"coordinates": [24.8301, 60.1866]}}]}
    # mock destination
    mock_dest = {"features": [{"geometry": {"coordinates": [24.9301, 60.2166]}}]}
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: mock_origin),
        MagicMock(status_code=200, json=lambda: mock_dest),
    ]

    origin, dest = digitransit.get_coordinates("Aalto-yliopisto", "Keilaniemi")
    assert origin == [24.8301, 60.1866]
    assert dest == [24.9301, 60.2166]

@patch("journey_service.digitransit.requests.post")
def test_query_journeys_success(mock_post):
    mock_response = {"data": {"planConnection": {"edges": []}}}
    mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

    result = digitransit.query_journeys([24.83, 60.18], [24.93, 60.21], "20250911084500")
    assert "planConnection" in result["data"]
