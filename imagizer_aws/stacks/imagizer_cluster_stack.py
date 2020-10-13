"""Imagizer Cluster Stack Module"""

import common
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3
)
from stacks import base_stack as base_stack_module

import variables


class ImagizerClusterStack(core.Stack):
    """
    Imagizer Cluster Stack
    """

    def __init__(self, scope: core.Construct, stack_id: str,
                 base_stack: base_stack_module.BaseStack, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        # Get the Imagizer JSON config user data
        self.user_data = common.get_imagizer_user_data()

        # Create the autoscaling group which will manage the Imagizer Instances
        self.asg = self.__create_asg(self.user_data, base_stack.vpc)

        # Create the load balancer which will route requests to the Imagizer instances
        self.target_group = self.__create_application_target_group(self.asg, base_stack.vpc)
        self.load_balancer = self.__create_application_load_balancer(self.target_group, base_stack.vpc)

        # Setup the Auto Scaling Group scaling policy
        self.__create_asg_scaling_policy(self.asg)
        self.__create_asg_perms(self.asg)
        self.__create_asg_firewall(self.asg)

    def __create_asg(self, user_data: str, vpc: ec2.Vpc):
        subnets = ec2.SubnetSelection(one_per_az=True, subnet_type=ec2.SubnetType.PUBLIC)
        asg = autoscaling.AutoScalingGroup(
            self,
            id=common.generate_id("ImagizerAutoscalingGroup"),
            vpc=vpc,
            vpc_subnets=subnets,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass[variables.ASG_INSTANCE_TYPE],
                instance_size=ec2.InstanceSize[variables.ASG_INSTANCE_SIZE]
            ),
            machine_image=ec2.GenericLinuxImage(ami_map={self.region: variables.IMAGIZER_AMI_ID}),
            user_data=ec2.UserData.custom(user_data),
            update_type=autoscaling.UpdateType.ROLLING_UPDATE,
            health_check=autoscaling.HealthCheck.ec2(
                grace=core.Duration.seconds(variables.ASG_HEALTH_CHECK_GRACE_PERIOD)
            ),
            cooldown=core.Duration.seconds(variables.ASG_HEALTH_CHECK_GRACE_PERIOD),
            min_capacity=variables.ASG_MIN_CAPACITY,
            max_capacity=variables.ASG_MAX_CAPACITY,
            rolling_update_configuration=autoscaling.RollingUpdateConfiguration(
                min_instances_in_service=variables.ASG_ROLL_OUT_BATCH_SIZE,
                max_batch_size=variables.ASG_ROLL_OUT_BATCH_SIZE,
                wait_on_resource_signals=True,
                pause_time=core.Duration.minutes(variables.ASG_ROLL_OUT_PATCH_MINUTES))
        )

        common.add_tags(self, asg, variables.IMAGIZER_CLUSTER_TAGS)
        return asg

    def __create_application_target_group(self, asg: autoscaling.AutoScalingGroup, vpc: ec2.Vpc):
        target_group = elbv2.ApplicationTargetGroup(self,
                                                    id=common.generate_id("ImagizerTargetGroup"),
                                                    targets=[asg],
                                                    port=variables.PUBLIC_PORT,
                                                    protocol=elbv2.ApplicationProtocol.HTTP,
                                                    vpc=vpc,
                                                    health_check=elbv2.HealthCheck(
                                                        path="/health",
                                                        healthy_threshold_count=2,
                                                        interval=core.Duration.seconds(10)
                                                    ))
        common.add_tags(self, target_group, variables.IMAGIZER_CLUSTER_TAGS)
        return target_group

    def __create_application_load_balancer(self, target_group: elbv2.ApplicationTargetGroup, vpc: ec2.Vpc):
        sub_nets = ec2.SubnetSelection(one_per_az=True, subnet_type=ec2.SubnetType.PUBLIC)
        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            id=common.generate_id("ImagizerLoadBalancer"),
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=sub_nets
        )

        listener = load_balancer.add_listener(common.generate_id("ImagizerHTTPListener"),
                                              port=variables.PUBLIC_PORT,
                                              protocol=elbv2.ApplicationProtocol.HTTP)
        listener.add_target_groups(common.generate_id("ImagizerTargetGroup"), target_groups=[target_group])
        common.add_tags(self, load_balancer, variables.IMAGIZER_CLUSTER_TAGS)

        core.CfnOutput(self, common.generate_id("ImagizerClusterEndpointOutput"),
                       export_name="Endpoint",
                       value="http://" + load_balancer.load_balancer_dns_name)

        return load_balancer

    @staticmethod
    def __create_asg_scaling_policy(asg):
        cpu_utilization = cloudwatch.Metric(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions={"AutoScalingGroupName": asg.auto_scaling_group_name},
            period=core.Duration.minutes(15)
        )

        asg.scale_on_metric(
            "ImagizerClusterCpuTarget",
            metric=cpu_utilization,
            adjustment_type=autoscaling.AdjustmentType.CHANGE_IN_CAPACITY,
            estimated_instance_warmup=core.Duration.seconds(400),
            scaling_steps=[
                autoscaling.ScalingInterval(change=variables.ASG_CAPACITY_INCREASE,
                                            lower=variables.ASG_CPU_HIGH_THRESHOLD),
                autoscaling.ScalingInterval(change=-variables.ASG_CAPACITY_DECREASE,
                                            upper=variables.ASG_CPU_LOW_THRESHOLD)
            ]
        )

        asg.scale_on_request_count(
            "ImagizerClusterRpsTarget",
            target_requests_per_second=variables.ASG_RPS_THRESHOLD,
            disable_scale_in=True
        )

    @staticmethod
    def __create_asg_perms(asg):
        asg.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "ec2:DescribeInstances",
                "autoscaling:DescribeAutoScalingGroups",
                "elasticloadbalancing:DescribeTargetHealth"
            ]
        ))

    @staticmethod
    def __create_asg_firewall(asg):
        for port in variables.PRIVATE_PORTS:
            asg.connections.allow_internally(ec2.Port.tcp(port))
            asg.connections.allow_from(ec2.Peer.ipv4(variables.VPC_CIDR), ec2.Port.tcp(port),
                                       "Known internal EC2 servers")
            for cidr in variables.DEVELOPER_CIDR:
                asg.connections.allow_from(ec2.Peer.ipv4(cidr), ec2.Port.tcp(port),
                                           "Developer IPs")
