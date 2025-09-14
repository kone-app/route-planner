import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
from datetime import datetime, timedelta

from .digitransit import get_coordinates, query_journeys
from .filters import filter_journeys
from .notifier import send_email

logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="JourneyNotification", service="JourneyService")


def start(origin, destination, arriveBy):

    # Parse incoming arriveBy string (yyyyMMddHHmmss)
    dt = datetime.strptime(arriveBy, "%Y%m%d%H%M%S")

    # If weekend, shift to Monday
    if dt.weekday() == 5:   # Saturday
        dt += timedelta(days=2)
        logger.info("Adjusted arriveBy from Saturday -> Monday")
    elif dt.weekday() == 6: # Sunday
        dt += timedelta(days=1)
        logger.info("Adjusted arriveBy from Sunday -> Monday")

    arriveBy = dt.strftime("%Y%m%d%H%M%S")

    origin_coordinates, destination_coordinates = get_coordinates(origin, destination)
    api_response = query_journeys(origin_coordinates, destination_coordinates, arriveBy)
    journeys = filter_journeys(result=api_response, origin=origin, destination=destination)
    email_status = send_email(body_text=journeys)
    return {"Journeys": journeys, "Email Status": email_status}

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        origin = params.get("origin")
        destination = params.get("destination")
        arriveBy = params.get("arriveBy")

        if not origin or not destination or not arriveBy:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing origin, destination, or arriveBy"})
            }

        result = start(origin, destination, arriveBy)
        metrics.add_metric(name="JourneyEmailsSent", unit=MetricUnit.Count, value=1)
        return {"statusCode": 200, "body": json.dumps({"message": result})}

    except Exception as e:
        logger.exception("Error processing request")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
