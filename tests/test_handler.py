import json
import pytest
from journey_service import handler


# Fake AWS Lambda context
class FakeContext:
    function_name = "JourneyServiceFunction"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:local:0:function:JourneyServiceFunction"
    aws_request_id = "fake-request-id"


def make_event(params=None, path="/journeys"):
    """Helper to create a fake API Gateway event"""
    return {
        "httpMethod": "GET",
        "path": path,
        "queryStringParameters": params or {},
    }


def test_lambda_handler_missing_params():
    """Should return 400 when query params are missing"""
    event = make_event({})
    result = handler.lambda_handler(event, FakeContext())
    body = json.loads(result["body"])

    assert result["statusCode"] == 400
    assert "error" in body


def test_lambda_handler_valid(monkeypatch):
    """Should return 200 and include Journeys when start() succeeds"""

    def fake_start(origin, dest, arriveBy):
        return {"Journeys": ["mocked journey"], "Email Status": "Sent"}

    monkeypatch.setattr(handler, "start", fake_start)

    event = make_event(
        {"origin": "Aalto-yliopisto", "destination": "Keilaniemi", "arriveBy": "20250911084500"}
    )
    result = handler.lambda_handler(event, FakeContext())
    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert "Journeys" in body["message"]
    assert body["message"]["Email Status"] == "Sent"


def test_lambda_handler_error(monkeypatch):
    """Should return 500 when start() raises an exception"""

    def fake_start(origin, dest, arriveBy):
        raise RuntimeError("Boom!")

    monkeypatch.setattr(handler, "start", fake_start)

    event = make_event(
        {"origin": "Aalto-yliopisto", "destination": "Keilaniemi", "arriveBy": "20250911084500"}
    )
    result = handler.lambda_handler(event, FakeContext())
    body = json.loads(result["body"])

    assert result["statusCode"] == 500
    assert "error" in body
    assert "Boom!" in body["error"]


def test_lambda_handler_invalid_path():
    """Should return 404 when path does not match any route"""
    event = make_event({"origin": "X"}, path="/unknown")
    result = handler.lambda_handler(event, FakeContext())

    # ApiGatewayResolver automatically returns 404
    assert result["statusCode"] == 404
    assert "Not Found" in result["body"]
