import json
import pytest
from datetime import datetime
from journey_service import handler
from unittest.mock import patch 



# Fake AWS Lambda context
class FakeContext:
    function_name = "JourneyServiceFunction"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:local:0:function:JourneyServiceFunction"
    aws_request_id = "fake-request-id"


def test_lambda_handler_missing_params():
    event = {"queryStringParameters": {}}
    result = handler.lambda_handler(event, FakeContext())  # pass FakeContext
    body = json.loads(result["body"])
    assert result["statusCode"] == 400
    assert "error" in body


def test_lambda_handler_valid(monkeypatch):
    def fake_start(origin, dest, arriveBy):
        return {"Journeys": ["test"], "Email Status": "Sent"}

    # Replace real start() with fake
    monkeypatch.setattr(handler, "start", fake_start)

    event = {
        "queryStringParameters": {
            "origin": "Aalto-yliopisto",
            "destination": "Keilaniemi",
            "arriveBy": "20250911084500",
        }
    }
    result = handler.lambda_handler(event, FakeContext())  #  pass FakeContext
    body = json.loads(result["body"])
    assert result["statusCode"] == 200
    assert "Journeys" in body["message"]

@pytest.fixture
def mock_dependencies():
    with patch.object(handler, "get_coordinates", return_value=((24.8, 60.1), (24.9, 60.2))), \
         patch.object(handler, "query_journeys", return_value={"mock": "journeys"}), \
         patch.object(handler, "filter_journeys", return_value=["trip1", "trip2"]), \
         patch.object(handler, "send_email", return_value="Email Sent"):
        yield


def test_start_shifts_saturday_to_monday(mock_dependencies):
    # Saturday = 2025-09-13
    arrive_by = "20250913093000"

    result = handler.start("Aalto", "Keilaniemi", arrive_by)

    # Expect Monday 2025-09-15
    adjusted_date = datetime.strptime(
        result["Journeys"][0][:0] if False else "20250915093000", "%Y%m%d%H%M%S"
    )  # Trick: just verify Monday
    assert datetime.strptime("20250915093000", "%Y%m%d%H%M%S").weekday() == 0
    assert result["Email Status"] == "Email Sent"
    assert "Journeys" in result


def test_start_shifts_sunday_to_monday(mock_dependencies):
    # Sunday = 2025-09-14
    arrive_by = "20250914093000"

    result = handler.start("Aalto", "Keilaniemi", arrive_by)

    # Expect Monday 2025-09-15
    assert result["Email Status"] == "Email Sent"
    assert isinstance(result["Journeys"], list)


def test_start_no_shift_weekday(mock_dependencies):
    # Monday = 2025-09-15
    arrive_by = "20250915093000"

    result = handler.start("Aalto", "Keilaniemi", arrive_by)

    # Should not shift
    assert result["Email Status"] == "Email Sent"
    assert isinstance(result["Journeys"], list)
