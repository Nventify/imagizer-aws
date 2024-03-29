"""Base Stack Module"""
# pylint: disable=R0913,R0902

from imagizer_aws import common
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)

from imagizer_aws import variables


class BaseStack(Stack):
    """
    Base Stack

    The base stack includes the basic components for a regional base such as VPC,
     Subnets, DNS records, SSL certs, etc.
    """

    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        # Create the base VPC
        self.vpc = self.__create_vpc()

    def __create_vpc(self):
        vpc = ec2.Vpc(self,
                      common.generate_id("Vpc"),
                      ip_addresses=ec2.IpAddresses.cidr(variables.VPC_CIDR),
                      max_azs=variables.MAX_AVAILABILITY_ZONES,
                      nat_gateways=1)
        common.add_tags(self, vpc, [{
            "name": "Name",
            "value": common.generate_id("Vpc")
        }])
        return vpc
