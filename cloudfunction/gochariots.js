var querystring = require('querystring');
var http = require('http');
var fs = require('fs');
var fnv = require('fnv-plus');

var host;
var port;

exports.setHost = function(url) {
    var s = url.split(':')
    host = s[0]
    port = s[1]
}

exports.getHash = function(record) {
    var result = []
    for (var key in record.tags) {
        var value = record.tags[key]
        var h = fnv.hash(key + ':' + value, 64)
        result.push(h.dec())
    }
    return result
}


exports.post = function(record) {
    if (!host || typeof host == 'undefined' || !port || typeof port == 'undefined') {
        console.log('Host not set yet')
        return
    }
    
    var body = JSON.stringify(record.toDict())
    body = body.slice(0, body.indexOf('"prehash"') + 10) + body.slice(body.indexOf('"prehash"') + 11, body.length)
    body = body.slice(0, body.indexOf('"', body.indexOf('"prehash"') + 10)) + body.slice(body.indexOf('"', body.indexOf('"prehash"') + 10) + 1, body.length)
    body = body.slice(0, body.indexOf('"seed"') + 7) + body.slice(body.indexOf('"seed"') + 8, body.length)
    body = body.slice(0, body.indexOf('"', body.indexOf('"seed"') + 7)) + body.slice(body.indexOf('"', body.indexOf('"seed"') + 7) + 1, body.length)
    var request = new http.ClientRequest({
        host: host,
        port: port,
        path: '/record',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body)
        }
    })
    request.end(body)
    request.on('response', function (response) {
        console.log('STATUS: ' + response.statusCode);
        console.log('HEADERS: ' + JSON.stringify(response.headers));
        response.setEncoding('utf8');
        response.on('data', function (chunk) {
            console.log('BODY: ' + chunk);
        });
    });
}