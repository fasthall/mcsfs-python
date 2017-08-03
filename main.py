import uuid
import json
import store
from secretsharing import PlaintextToHexSecretSharer
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def mcsfs():
    if request.method == 'POST':
        if 'secret' in request.form:
            secret = str(request.form['secret'])
        elif 'secret' in request.files:
            secret = str(request.files['secret'].read())
        else:
            return 'secret not found in request'
        access_key = str(uuid.uuid4())
        try:
            shares = PlaintextToHexSecretSharer.split_secret(secret, 2, 3)
        except ValueError as e:
            return str(e)
        store.upload_s3(access_key, shares[0])
        store.upload_gcp(access_key, shares[1])
        store.upload_azure(access_key, shares[2])
        return access_key
    elif request.method == 'GET':
        if 'key' not in request.form:
            return 'key not found in form'
        key = str(request.form['key'])
        share_s3 = store.download_s3(key)
        share_gcp = store.download_gcp(key)
        share_azure = store.download_azure(key)
        shares = []
        if share_s3:
            shares.append(share_s3)
        if share_gcp:
            shares.append(share_gcp)
        if share_azure:
            shares.append(share_azure)
        secret = PlaintextToHexSecretSharer.recover_secret(shares)
        return secret
    return 'POST to encrypt, GET to decrypt'

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int('8080'),
        debug=True
    )