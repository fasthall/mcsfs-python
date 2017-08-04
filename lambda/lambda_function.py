import gochariots
import boto3
import os
import json
import shutil
import uuid

gochariots.setHost(os.environ['GOCHARIOTS_HOST'])
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    path = '/tmp/'
    try:
        os.makedirs(path)
    except:
        pass
    s3.download_file(bucket, key, path + key)
    with open(path + key, 'r') as data:
        data = data.read().split('\n')
    share = data[0]
    hash = data[1]

    content = {'action': 'Uploaded_S3', 'bucket': bucket, 'key': key, 'share': share}
    r1 = gochariots.Record(int(key))
    r1.add('mcsfs', json.dumps(content))
    r1.setHash(int(hash))
    result = gochariots.post(r1)

    return 'Record posted'