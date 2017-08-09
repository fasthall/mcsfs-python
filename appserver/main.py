import os
import uuid
import json
import time
import store
import config
import gochariots
import threading
import Queue
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
        s3_thread = threading.Thread(target=store.upload_s3, args=(access_key, shares[0] + '\n' + str(hash2),))
        gcp_thread = threading.Thread(target=store.upload_gcp, args=(access_key, shares[1] + '\n' + str(hash2),))
        azure_thread = threading.Thread(target=store.upload_azure, args=(access_key, shares[2] + '\n' + str(hash2),))
        s3_thread.start()
        gcp_thread.start()
        azure_thread.start()
        s3_thread.join()
        gcp_thread.join()
        azure_thread.join()
        
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

        que = Queue.Queue()
        s3_thread = threading.Thread(target=store.download_s3, args=(que, key))
        s3_thread.start()
        gcp_thread = threading.Thread(target=store.download_gcp, args=(que, key))
        gcp_thread.start()
        azure_thread = threading.Thread(target=store.download_azure, args=(que, key))
        azure_thread.start()

        shares = []
        while len(shares) < 2:
            shares.append(que.get())

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