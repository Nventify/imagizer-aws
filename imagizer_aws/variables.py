ENV = "production"
REGION = "us-west-1"

# Imagizer AMI ID
IMAGIZER_AMI_ID = ""

# VPC
VPC_CIDR = "10.1.0.0/24"
MAX_AVAILABILITY_ZONES = 4

# Auto Scaling Group
ASG_MIN_CAPACITY = 3  # Minimum number of imagizer instances
ASG_MAX_CAPACITY = 40  # Maximum number of imagizer instances
ASG_INSTANCE_TYPE = "STANDARD5"  # M5
ASG_INSTANCE_SIZE = "XLARGE2"  # 2xlarge - We recommend the m5.2xlarge instance type
ASG_ROLL_OUT_BATCH_SIZE = 1  # Control the batch size during updates. Allows for zero downtime during updates.
ASG_ROLL_OUT_PATCH_MINUTES = 3
ASG_RPS_THRESHOLD = 3000  # Capacity will increase when RPS passes this threshold
ASG_CPU_HIGH_THRESHOLD = 65  # Capacity will increase when average CPU passes this threshold
ASG_CPU_LOW_THRESHOLD = 30  # Capacity will decrease when average CPU drops below this threshold
ASG_CAPACITY_INCREASE = 2  # Increase the capacity in steps of N
ASG_CAPACITY_DECREASE = 1  # Decrease the capacity in steps of N
ASG_HEALTH_CHECK_GRACE_PERIOD = 300  # The autoscaling group will wait for N seconds before checking health
RPS_SCALE_IN_EVALUATION_PERIOD = 300  # Requests per second scale in evaluation period
ERRORS_SCALE_OUT_EVALUATION_PERIOD = 120  # Errors scale out evaluation period
ERRORS_COUNT_PER_PERIOD = 200

# Firewall
PUBLIC_PORT = 80
PRIVATE_PORTS = [
    80,
    81,
    17001,
    17004,
    17005,
    17006,
    17007,
    17009,
    9100
]
DEVELOPER_CIDR = []  # Whitelist IP CIDR addresses which should have access to all ports above

# Tags to be added to all resources
IMAGIZER_CLUSTER_TAGS = [
    {
        "name": "Name",
        "value": "imagizer"
    },
    {
        "name": "env",
        "value": ENV
    },
    {
        "name": "spot-enabled",  # Enable AutoSpotting
        "value": "true"
    }
]

# Auto Spotting
# Lambda that replaces on-demand instances with spot instances
# See https://github.com/AutoSpotting/AutoSpotting for more information
AUTO_SPOTTING_ENABLED = False
AUTO_SPOTTING_LICENSE = "evaluation"  # Change this to "I_am_supporting_it_on_Patreon" when using the paid plan
AUTO_SPOTTING_TEMPLATE_URL = "https://s3.amazonaws.com/cloudprowess/nightly/template_build_1139.yaml"
AUTO_SPOTTING_ALLOW_INSTANCE_TYPES = "m4.xlarge,m4.xlarge,m4.2xlarge,m4.4xlarge,m5.xlarge,m5.2xlarge,m5.4xlarge"
AUTO_SPOTTING_ALLOW_REGIONS = "us-east-1 us-west-2"
AUTO_SPOTTING_PRICE_BUFFER = "25.0"
