import json
import pytest
from journey_service import handler


# Fake AWS Lambda context
class FakeContext:
    function_name = "JourneyServiceFunction"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:local:0:function:JourneyServiceFunction"
    aws_request_id = "fake-request-id"


def test_lambda_handler_missing_params():
    event = {"queryStringParameters": {}}
    result = handler.lambda_handler(event, FakeContext())  # 👈 pass FakeContext
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
    result = handler.lambda_handler(event, FakeContext())  # 👈 pass FakeContext
    body = json.loads(result["body"])
    assert result["statusCode"] == 200
    assert "Journeys" in body["message"]
