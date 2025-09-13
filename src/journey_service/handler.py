import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from aws_lambda_powertools.event_handler.api_gateway import Response

from .digitransit import get_coordinates, query_journeys
from .filters import filter_journeys
from .notifier import send_email

logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="JourneyNotification", service="JourneyService")
app = ApiGatewayResolver()


def start(origin, destination, arriveBy):
    """Business logic: fetch coords, query Digitransit, filter journeys, send email"""
    origin_coordinates, destination_coordinates = get_coordinates(origin, destination)
    api_response = query_journeys(origin_coordinates, destination_coordinates, arriveBy)
    journeys = filter_journeys(result=api_response, origin=origin, destination=destination)
    email_status = send_email(body_text=journeys)
    return {"Journeys": journeys, "Email Status": email_status}


# Define GET /journeys route
@app.get("/journeys")
def get_journeys():
    origin = app.current_event.get_query_string_value("origin")
    destination = app.current_event.get_query_string_value("destination")
    arriveBy = app.current_event.get_query_string_value("arriveBy")

    if not origin or not destination or not arriveBy:
        raise BadRequestError("Missing origin, destination, or arriveBy")

    try:
        result = start(origin, destination, arriveBy)
        metrics.add_metric(name="JourneyEmailsSent", unit=MetricUnit.Count, value=1)
        return {"statusCode": 200, "body": json.dumps({"message": result})}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.exception_handler(BadRequestError)
def handle_bad_request(ex: BadRequestError):
    return Response(
        status_code=400,
        content_type="application/json",
        body=json.dumps({"detail": str(ex)})
    )


# Lambda entrypoint
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    return app.resolve(event, context)
