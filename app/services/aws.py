import boto3
from boto3.resources.base import ServiceResource
from fastapi import Depends
from app.core.config import settings

# def get_s3_resource():
#     s3_resource: ServiceResource = boto3.client(
#         "s3",
#         region_name=settings.AWS_REGION,
#         aws_access_key_id=settings.AWS_KEY,
#         aws_secret_access_key=settings.AWS_SECRET,
#     )

#     return s3_resource

def get_client(name: str):
    rds_client = boto3.client(
        name, #"s3", "rds",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
    )

    return rds_client
