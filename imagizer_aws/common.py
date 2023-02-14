"""Common code"""
# pylint: disable=R0913,R0903

import os

import sys
import aws_cdk as cdk

from imagizer_aws import variables

USER_DATA = os.path.dirname(os.path.realpath(sys.argv[0])) + "/imagizer_aws/imagizer-config.json"


def get_imagizer_user_data():
    """Returns an Imagizer JSON config string from filename"""
    file = open(USER_DATA, mode='r')
    user_data = file.read()
    file.close()
    return user_data


def generate_id(name, env=None):
    """Generates an ID name"""
    if not env:
        env = variables.ENV.title()
    return name + env


def add_tags(context, resource, extras_tags=None):
    """Add tags to given resource"""
    cdk.Tags.of(resource).add(key="region", value=context.region, apply_to_launched_instances=True)

    if not any(tag.get('name', None) == 'env' for tag in extras_tags):
        cdk.Tags.of(resource).add(key="env", value=variables.ENV, apply_to_launched_instances=True)

    if extras_tags:
        for tag in extras_tags:
            cdk.Tags.of(resource).add(key=tag['name'], value=tag['value'], apply_to_launched_instances=True)
