const crypto = require("crypto");

const _hash = x =>
  crypto
    .createHash("sha512")
    .update(x)
    .digest("hex")
    .toLowerCase();

module.exports = {
  calculateAddress(family, name) {
    const PREFIX = _hash(family).substring(0, 6);
    let address = PREFIX + _hash(name).slice(-64);
    return address;
  },

  calculateAddresses(family, args) {
    const PREFIX = _hash(family).substring(0, 6);
    let addresses = [];

    for (let key in args) {
      let address = PREFIX + _hash(args[key]).slice(-64);
      addresses.push(address);
    }
    return addresses;
  },

  // Encoding helpers and constants
  getAddress(key, length) {
    return _hash(key).slice(0, length || 64);
  }
};
