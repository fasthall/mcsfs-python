function Record(seed) {
    this.tags = {};
    this.seed = seed;
    this.hash = '0';
}

Record.prototype.setHash = function(hash) {
    this.hash = hash;
}

Record.prototype.add = function(key, value) {
    this.tags[key] = value;
}

Record.prototype.toDict = function() {
    r = {"seed": this.seed, "prehash": this.hash, "tags": this.tags};
    return r;
}

module.exports = Record;