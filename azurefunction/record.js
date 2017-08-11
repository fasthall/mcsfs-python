function Record(seed) {
    this.tags = {};
    this.seed = seed;
    this.hash = [];
}

Record.prototype.addHash = function(hash) {
    this.hash.push(hash);
}

Record.prototype.add = function(key, value) {
    this.tags[key] = value;
}

Record.prototype.toDict = function() {
    if (typeof this.seed == 'number') {
        r = {"seed": this.seed, "strhash": this.hash, "tags": this.tags};
    } else if (typeof this.seed == 'string') {
        r = {"strseed": this.seed, "strhash": this.hash, "tags": this.tags};
    }
    return r;
}

module.exports = Record;