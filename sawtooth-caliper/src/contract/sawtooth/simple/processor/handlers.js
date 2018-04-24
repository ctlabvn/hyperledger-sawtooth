// SPDX-License-Identifier: Apache-2.0

/* 
This code was written by Zac Delventhal @delventhalz.
Original source code can be found here: https://github.com/delventhalz/transfer-chain-js/blob/master/processor/handlers.js
 */

"use strict";

const { TransactionHandler } = require("sawtooth-sdk/processor/handler");
const { InvalidTransaction } = require("sawtooth-sdk/processor/exceptions");
const { TransactionHeader } = require("sawtooth-sdk/protobuf");
const cbor = require("cbor");
const {
  calculateAddress,
  calculateAddresses,
  getAddress
} = require("../../../../../lib/sawtooth/address");

const FAMILY = "simple";
const PREFIX = getAddress(FAMILY, 6);

// const getAssetAddress = name => PREFIX + "00" + getAddress(name, 62);
const getAssetAddress = name => calculateAddress(FAMILY, name);
const encode = obj => Buffer.from(JSON.stringify(obj, Object.keys(obj).sort()));
const decode = buf => JSON.parse(buf.toString());

// Add a new asset to state
const openAccount = (owner, asset, context) => {
  const address = getAssetAddress(owner);
  return context.getState([address]).then(entries => {
    const entry = entries[address];
    if (entry && entry.length > 0) {
      // throw new InvalidTransaction("Account in use");
      // allow update state to test the transaction through put
      console.log("Account in use, need overridden");
    }

    return context.setState({
      [address]: encode({ asset, owner })
    });
  });
};

// Handler for JSON encoded payloads
class JSONHandler extends TransactionHandler {
  constructor() {
    console.log("Initializing JSON handler for simple chain");
    super(FAMILY, ["1.0"], [PREFIX]);
  }

  apply(txn, context) {
    // Parse the transaction header and payload
    const header = txn.header;
    const signer = header.signerPublicKey;
    const data = cbor.decode(txn.payload);

    // const data = JSON.parse(txn.payload);
    for (let item of data) {
      const { verb: action, money: asset, account: owner } = item;

      // Call the appropriate function based on the payload's action
      console.log(
        `Handling transaction:  ${action} > ${asset}`,
        owner ? `> ${owner.slice(0, 8)}... ` : "",
        `:: ${signer.slice(0, 8)}...`
      );
      // queries do not affect on the assets
      switch (action) {
        case "open":
          return openAccount(owner, asset, context);
        default:
          return Promise.resolve().then(() => {
            throw new InvalidTransaction('Action must be "open"');
          });
      }
    }
  }
}

module.exports = {
  JSONHandler
};
