import json
import pytest
import handler


class FakeContext:
    function_name = "test"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:test"
    aws_request_id = "test"


def make_event(query_params=None, path="/journeys"):
    return {
        "resource": path,
        "path": path,
        "httpMethod": "GET",
        "queryStringParameters": query_params,
    }


def test_lambda_handler_valid(monkeypatch):
    """ Should return 200 and Journeys when start() succeeds"""

    def fake_start(origin, dest, arriveBy):
        return {"Journeys": ["mocked journey"], "Email Status": "Sent"}

    monkeypatch.setattr(handler, "start", fake_start)

    event = make_event(
        {"origin": "Aalto-yliopisto", "destination": "Keilaniemi", "arriveBy": "20250911084500"}
    )
    result = handler.lambda_handler(event, FakeContext())

    assert result["statusCode"] == 200
    parsed_body = json.loads(result["body"])
    assert "Journeys" in parsed_body["message"]
    assert parsed_body["message"]["Journeys"] == ["mocked journey"]
    assert parsed_body["message"]["Email Status"] == "Sent"


def test_lambda_handler_missing_params():
    """ Should return 400 when query params are missing"""
    event = make_event({"origin": "OnlyOrigin"})  # missing destination + arriveBy
    result = handler.lambda_handler(event, FakeContext())

    assert result["statusCode"] == 400
    parsed_body = json.loads(result["body"])
    assert "detail" in parsed_body
    assert "Missing origin, destination, or arriveBy" in parsed_body["detail"]


def test_lambda_handler_start_raises(monkeypatch):
    """ Should return 500 when start() raises an exception"""

    def fake_start(origin, dest, arriveBy):
        raise RuntimeError("Unexpected failure")

    monkeypatch.setattr(handler, "start", fake_start)

    event = make_event(
        {"origin": "Aalto-yliopisto", "destination": "Keilaniemi", "arriveBy": "20250911084500"}
    )
    result = handler.lambda_handler(event, FakeContext())

    assert result["statusCode"] == 500
    parsed_body = json.loads(result["body"])
    assert "error" in parsed_body
    assert "Unexpected failure" in parsed_body["error"]


def test_direct_start_function(monkeypatch):
    """ Direct test of start() function with mocks"""

    monkeypatch.setattr(handler, "get_coordinates", lambda o, d: ("coords1", "coords2"))
    monkeypatch.setattr(handler, "query_journeys", lambda o, d, a: {"dummy": True})
    monkeypatch.setattr(handler, "filter_journeys", lambda result, origin, destination: ["f1", "f2"])
    monkeypatch.setattr(handler, "send_email", lambda body_text: "SentOK")

    result = handler.start("O", "D", "20250911084500")

    assert "Journeys" in result
    assert "Email Status" in result
    assert result["Journeys"] == ["f1", "f2"]
    assert result["Email Status"] == "SentOK"
