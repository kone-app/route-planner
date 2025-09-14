from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    CfnOutput,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,

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

        # Optional: Enable schedule if flag is set
        enable_schedule = os.getenv("ENABLE_SCHEDULE", "false").lower() == "true"
        if enable_schedule:
            rule = events.Rule(
                self,
                "DailyMorningRule",
                schedule=events.Schedule.cron(
                    minute=os.getenv("CRON_MINUTE", "0"),
                    hour=os.getenv("CRON_HOUR", "3"),         # 06:00 EEST = 03:00 UTC
                    week_day="MON-FRI"
                ),
            )
            rule.add_target(targets.LambdaFunction(journey_lambda))

        
        # S3 bucket for OpenAPI docs
        # ----------------------------
        bucket = s3.Bucket(
            self,
            "OpenApiDocsBucket",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
                block_public_policy=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,   # clean up in dev
            auto_delete_objects=True                    # clean up in dev
        )

        # Deploy openapi.yml into /docs in bucket
        s3deploy.BucketDeployment(
            self,
            "DeployOpenApi",
            sources=[s3deploy.Source.asset("./", exclude=["**", "!openapi.yml"])],  # only include openapi.yml
            destination_bucket=bucket,
            destination_key_prefix="docs",  # file will be at /docs/openapi.yml
        )

        # API Gateway route /docs -> serves openapi.yml from S3
        docs_resource = api.root.add_resource("docs")
        docs_resource.add_method(
            "GET",
            apigateway.HttpIntegration(
                f"http://{bucket.bucket_website_domain_name}/docs/openapi.yml"
            ),
        )

        # CloudFormation outputs
        CfnOutput(self, "OpenApiS3Url", value=f"http://{bucket.bucket_website_domain_name}/docs/openapi.yml")

        # Outputs
        if enable_schedule:  # only output if created
            CfnOutput(self, "EventRuleName", value=rule.rule_name)
               
        # Output useful info after deploy
        CfnOutput(self, "ApiEndpoint", value=api.url)
        CfnOutput(self, "LambdaName", value=journey_lambda.function_name)
        
