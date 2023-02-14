"""AutoSpotting Stack Module"""
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_cloudformation as cf
)

from imagizer_aws import variables


class AutoSpottingStack(Stack):
    """
    Auto Spotting: Significantly lower our Amazon AWS costs by automating the use of spot instances.
    https://github.com/AutoSpotting/AutoSpotting

    All autoscaling groups with the tag 'spot-enabled' will be subject to auto spotting.
    """

    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        if variables.AUTO_SPOTTING_ENABLED:
            self.auto_spotting_cf = self.launch_auto_spotting_cf()

    def launch_auto_spotting_cf(self):
        """Launch Auto Spotting Cloud formation"""
        return cf.CfnStack(self, "AutoSpotting",
                           template_url=variables.AUTO_SPOTTING_TEMPLATE_URL,
                           parameters={
                               "AllowedInstanceTypes": variables.AUTO_SPOTTING_ALLOW_INSTANCE_TYPES,
                               "Regions": variables.AUTO_SPOTTING_ALLOW_REGIONS,
                               "SpotPricePercentageBuffer": variables.AUTO_SPOTTING_PRICE_BUFFER,
                               "License": variables.AUTO_SPOTTING_LICENSE
                           })
