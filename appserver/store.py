import config
import boto3
import uuid
import os
from google.cloud import storage
from azure.storage.blob import BlockBlobService

s3_client = boto3.resource('s3', aws_access_key_id=config.AWS_KEY_ID, aws_secret_access_key=config.AWS_ACCESS_LEY, region_name=config.AWS_REGION)
gcp_client = storage.Client.from_service_account_json('./cred.json')
azure_client = BlockBlobService(account_name=config.AZURE_ACCOUNT_NAME, account_key=config.AZURE_ACCOUNT_KEY)

def upload_s3(key, share):
    s3_client.Bucket(config.S3_BUCKET).put_object(Key=key, Body=share)

def upload_gcp(key, share):
    bucket = gcp_client.get_bucket(config.GCP_BUCKET)
    blob = bucket.blob(key)
    blob.upload_from_string(share)

def upload_azure(key, share):
    azure_client.create_blob_from_bytes(config.AZURE_CONTAINER, key, share)

def download_s3(key):
    tmp_file = str(uuid.uuid4())
    s3_client.Bucket(config.S3_BUCKET).download_file(key, tmp_file)
    with open(tmp_file, 'r') as data:
        data = data.read().split('\n')
    os.remove(tmp_file)
    return data[0], data[1]

def download_gcp(key):
    bucket = gcp_client.get_bucket(config.GCP_BUCKET)
    blob = bucket.blob(key)
    content = blob.download_as_string()
    content = content.split('\n')
    return content[0], content[1]

def download_azure(key):
    content = str(block_blob_service.get_blob_to_text(config.AZURE_CONTAINER, key).content).split('\n')
    return content[0], content[1]