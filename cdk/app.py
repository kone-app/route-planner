#!/usr/bin/env python3
import aws_cdk as cdk
from routing_stack import RoutingStack

app = cdk.App()

RoutingStack(
    app,
    "RoutePlannerStack",
    env=cdk.Environment(
        account="891376978717",   # 👈 your AWS account ID
        region="us-east-1"        # 👈 your AWS region
    ),
)

app.synth()
