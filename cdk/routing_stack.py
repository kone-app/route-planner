from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    CfnOutput,
)
from constructs import Construct
import os


class RoutingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function from Docker image (built from your Dockerfile)
        journey_lambda = _lambda.DockerImageFunction(
            self,
            "JourneyServiceFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=os.path.join(os.getcwd()),  # root dir containing Dockerfile
                file="Dockerfile",
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            environment={   #  inject env vars into container
                "DIGITRANSIT_API_KEY": os.getenv("DIGITRANSIT_API_KEY", ""),
                "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
                "TO_EMAIL": os.getenv("TO_EMAIL", ""),
                "GMAIL_APP_PASSWORD": os.getenv("GMAIL_APP_PASSWORD", ""),
                "GEO_CODING_URL": os.getenv(
                    "GEO_CODING_URL", "https://api.digitransit.fi/geocoding/v1/search"
                ),
                "ROUTING_URL": os.getenv(
                    "ROUTING_URL", "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
                ),
            },
        )

        # API Gateway REST API with Lambda integration
        api = apigateway.LambdaRestApi(
            self,
            "JourneyApi",
            handler=journey_lambda,
            proxy=False,
        )

        # /journeys endpoint
        journeys = api.root.add_resource("journeys")
        journeys.add_method("GET")

        # Output useful info after deploy
        CfnOutput(self, "ApiEndpoint", value=api.url)
        CfnOutput(self, "LambdaName", value=journey_lambda.function_name)
