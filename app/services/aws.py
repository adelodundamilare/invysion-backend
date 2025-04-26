import boto3
from boto3.resources.base import ServiceResource
from fastapi import Depends
from app.core.config import settings
from botocore.config import Config

# def get_s3_resource():
#     s3_resource: ServiceResource = boto3.client(
#         "s3",
#         region_name=settings.AWS_REGION,
#         aws_access_key_id=settings.AWS_KEY,
#         aws_secret_access_key=settings.AWS_SECRET,
#     )

#     return s3_resource

def get_client(name: str):
    custom_config = Config(
        connect_timeout=10,
        read_timeout=300
    )

    rds_client = boto3.client(
        name, #"s3", "rds",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
        config=custom_config
    )

    return rds_client
