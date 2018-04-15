const crypto = require("crypto");

const _hash = x =>
  crypto
    .createHash("sha512")
    .update(x)
    .digest("hex")
    .toLowerCase();

module.exports = {
  calculateAddress(family, name) {
    const INT_KEY_NAMESPACE = _hash(family).substring(0, 6);
    let address = INT_KEY_NAMESPACE + _hash(name).slice(-64);
    return address;
  },

  calculateAddresses(family, args) {
    const INT_KEY_NAMESPACE = _hash(family).substring(0, 6);
    let addresses = [];

    for (let key in args) {
      let address = INT_KEY_NAMESPACE + _hash(args[key]).slice(-64);
      addresses.push(address);
    }
    return addresses;
  }
};
