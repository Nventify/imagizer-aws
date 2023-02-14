# Imagizer AWS

This example project contains the [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html) Python code for provisioning an Imagizer Cluster on AWS. 

*Note: AWS CDK supports multiple languages. This project uses Python 3.*

## Getting Started

### Dependencies

Begin by installing the required dependencies. This project requires Python3, NodeJS, NPM, and the [AWS CLI](https://aws.amazon.com/cli/).
The AWS CLI must be configured with sufficient permissions to create AWS resources.

### Install

Run the following to compile and install the project.

```bash
# Install the AWS CDK
npm install --ignore-scripts

# Create a python virtual environment
python3 -m venv venv

# Install the Python dependencies
venv/bin/pip3 install -r requirements.txt

# Install the CDK Cli
npm install aws-cdk

# Active the Python environment
source venv/bin/activate
```

### Configure
- Modify the [imagizer_aws/variables.py](imagizer_aws/variables.py) file making note to add the Imagizer AMI ID.
- Modify the [imagizer_aws/imagizer-config.json](imagizer_aws/imagizer-config.json) to your needs while leaving the cluster configuration untouched to allow for Imagizer Clustering.

### Review Documentation

Review the documentation from AWS

- [Getting Started](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- [Working with the AWS CDK in Python](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html)
- [API Reference](https://docs.aws.amazon.com/cdk/api/latest/python/index.html)

## Usage

### Useful commands

 * `npx cdk ls`          list all stacks in the app
 * `npx cdk synth`       emits the synthesized CloudFormation template
 * `npx cdk deploy`      deploy this stack to your default AWS account/region
 * `npx cdk diff`        compare deployed stack with current state
 * `npx cdk docs`        open CDK documentation

### Deploy

Deploying will create a change set and apply any changes to the already provisioned AWS resources.

```bash
npx cdk deploy "*"
```

## Stacks
All stacks are located in the [imagizer_aws/stacks](imagizer_aws/stacks) folder.

### Base Stack
[imagizer_aws/stacks/base_stack.py](imagizer_aws/stacks/base_stack.py)

The Base stack includes the basic components for a regional base, such as a VPC, Subnets, DNS records, 
SSL certs, etc.

### Imagizer Cluster Stack
[imagizer_aws/stacks/imagizer_cluster_stack.py](imagizer_aws/stacks/imagizer_cluster_stack.py)

The Imagizer Cluster stack includes the resources to run a full Imagizer cluster such as an Autoscaling group of Imagizer EC2s and a load balancer.

### AutoSpotting Stack
[imagizer_aws/stacks/autospotting_stack.py](imagizer_aws/stacks/autospotting_stack.py)

Significantly lowers our Amazon AWS costs by automating the use of spot instances.
https://github.com/AutoSpotting/AutoSpotting

All autoscaling groups with the tag 'spot-enabled' will be subject to auto-spotting.
