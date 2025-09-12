#!/usr/bin/env python3
import aws_cdk as cdk
import os
from routing_stack import RoutingStack

app = cdk.App()

RoutingStack(
    app,
    "RoutePlannerStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),   # your AWS account ID
        region=os.getenv("CDK_DEFAULT_REGION")       # your AWS region
    ),
)

app.synth()
