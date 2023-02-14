#!/usr/bin/env python3

import os

from aws_cdk import App

from stacks.base_stack import BaseStack
from stacks.imagizer_cluster_stack import ImagizerClusterStack
from stacks.autospotting_stack import AutoSpottingStack

from imagizer_aws import variables

account = os.environ.get("ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"])
env = {"account": account, "region": variables.REGION}

app = App()

# Central Base (VPC and Networking)
base_stack = BaseStack(
    app,
    "ImagizerBase",
    env=env
)

# Imagizer Cluster
ImagizerClusterStack(
    app,
    "ImagizerCluster",
    base_stack=base_stack,
    env=env
)

# Auto Spotting
AutoSpottingStack(
    app,
    "AutoSpotting",
    env=env
)

app.synth()
