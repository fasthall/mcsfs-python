const storage = require('@google-cloud/storage')();

exports.processFile = function(event, callback) {
    console.log('Processing file: ' + event.data.name);
    let seed = event.data.name;
	
    let file = storage.bucket(event.data.bucket).file(event.data.name);
    file.download(
        function(err, content) {
            content = content.toString().split('\n');
            let share = content[0];
            let hash = content[1];
            
            var Record = require('./record');
            var gochariots = require('./gochariots');
            gochariots.setHost('')
            var r1 = new Record(seed);
            var dict = {
                action: 'Uploaded_GCP',
                key: event.data.name,
                share: share
            };
            r1.add('mcsfs', JSON.stringify(dict));
            r1.setHash(hash)
            gochariots.post(r1)
        }
    );
    
    callback();
};