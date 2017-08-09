const ACCOUNT_NAME = '';
const ACCOUNT_KEY = '';
const GOCHARIOTS_HOST = '';

module.exports = function(context, myBlob) {
    context.log('Processing file: ' + context.bindingData.name);
    let seed = context.bindingData.name;

    var storage = require('azure-storage');
    var blobService = storage.createBlobService(ACCOUNT_NAME, ACCOUNT_KEY);
    blobService.getBlobToText('mcsfs-python', seed, function(err, blobContent, blob) {
        if (err) {
            context.error(err);
        } else {
            context.log(blobContent)
            content = blobContent.toString().split('\n');
            let share = content[0];
            let hash = content[1];
            
            var Record = require('./record');
            var gochariots = require('./gochariots');
            gochariots.setHost(GOCHARIOTS_HOST)
            var r1 = new Record(seed);
            var dict = {
                action: 'Uploaded_Azure',
                key: seed,
                share: share
            };
            r1.add('mcsfs', JSON.stringify(dict));
            r1.setHash(hash);
            gochariots.post(r1);
        }
    });

    context.done()
};