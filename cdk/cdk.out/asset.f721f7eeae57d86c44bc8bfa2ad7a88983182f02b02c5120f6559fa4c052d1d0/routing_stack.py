from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
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
        journeys.add_method("GET")  # GET /journeys → Lambda
