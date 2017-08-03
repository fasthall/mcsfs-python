import config
import boto3
import os
from google.cloud import storage

s3_client = boto3.resource('s3', aws_access_key_id=config.AWS_KEY_ID, aws_secret_access_key=config.AWS_ACCESS_LEY, region_name=config.AWS_REGION)
gcp_client = storage.Client.from_service_account_json('./cred.json')

def upload_s3(key, share):
    s3_client.Bucket(config.S3_BUCKET).put_object(Key=key, Body=share)

def upload_gcp(key, share):
    bucket = gcp_client.get_bucket(config.GCP_BUCKET)
    blob = bucket.blob(key)
    blob.upload_from_string(share)

def upload_azure(key, share):
    pass

def download_s3(key):
    s3_client.Bucket(config.S3_BUCKET).download_file(key, key + '_s3')
    with open(key + '_s3', 'r') as data:
        share = data.read()
    os.remove(key + '_s3')
    return share

def download_gcp(key):
    bucket = gcp_client.get_bucket(config.GCP_BUCKET)
    blob = bucket.blob(key)
    return blob.download_as_string()

def download_azure(key):
    return None