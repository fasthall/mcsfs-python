import os
import uuid
import json
import time
import store
import config
import gochariots
from secretsharing import PlaintextToHexSecretSharer
from flask import Flask, request

app = Flask(__name__)
gochariots.setHost(config.GOCHARIOTS_HOST)

@app.route('/', methods=['GET', 'POST'])
def mcsfs():
    if request.method == 'POST':
        if 'secret' in request.form:
            secret = str(request.form['secret'])
        elif 'secret' in request.files:
            secret = str(request.files['secret'].read())
        else:
            return 'secret not found in request'
        seed = uuid.uuid1().int >> 64
        access_key = str(seed)

        content = {'action': 'POST', 'host': request.remote_addr, 'secret_length': len(secret), 'access_key': access_key}
        r1 = gochariots.Record(seed)
        r1.add('mcsfs', json.dumps(content))
        gochariots.post(r1)

        start = time.time()
        try:
            shares = PlaintextToHexSecretSharer.split_secret(secret, 2, 3)
        except ValueError as e:
            return str(e)

        content = {'action': 'Encrypted', 'shares': shares, 'elapsed_time': time.time() - start}
        r2 = gochariots.Record(seed)
        r2.add('mcsfs', json.dumps(content))
        r2.setHash(gochariots.getHash(r1)[0])
        gochariots.post(r2)
        hash2 = gochariots.getHash(r2)[0]

        start = time.time()
        store.upload_s3(access_key, shares[0] + '\n' + str(hash2))
        store.upload_gcp(access_key, shares[1] + '\n' + str(hash2))
        store.upload_azure(access_key, shares[2] + '\n' + str(hash2))
        
        content = {'action': 'Uploaded', 'elapsed_time': time.time() - start}
        r3 = gochariots.Record(seed)
        r3.add('mcsfs', json.dumps(content))
        r3.setHash(hash2)
        gochariots.post(r3)

        return access_key
    elif request.method == 'GET':
        if 'key' not in request.form:
            return 'key not found in form'
        key = str(request.form['key'])

        seed = uuid.uuid1().int >> 64
        content = {'action': 'GET', 'access_key': key}
        r1 = gochariots.Record(seed)
        r1.add('mcsfs', json.dumps(content))
        gochariots.post(r1)

        share_s3, _ = store.download_s3(key)
        share_gcp, _ = store.download_gcp(key)
        share_azure, _ = store.download_azure(key)
        shares = []
        if share_s3:
            shares.append(share_s3)
        if share_gcp:
            shares.append(share_gcp)
        if share_azure:
            shares.append(share_azure)

        content = {'action': 'Downloaded', 'shares': shares}
        r2 = gochariots.Record(seed)
        r2.add('mcsfs', json.dumps(content))
        r2.setHash(gochariots.getHash(r1)[0])
        gochariots.post(r2)
        
        secret = PlaintextToHexSecretSharer.recover_secret(shares)

        content = {'action': 'Decrypted', 'secret_length': len(secret)}
        r3 = gochariots.Record(seed)
        r3.add('mcsfs', json.dumps(content))
        r3.setHash(gochariots.getHash(r2)[0])
        gochariots.post(r3)

        return secret
    return 'POST to encrypt, GET to decrypt'

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int('8080'),
        debug=True
    )