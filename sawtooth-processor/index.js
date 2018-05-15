// SPDX-License-Identifier: Apache-2.0

/* 
This code was written by Zac Delventhal @delventhalz.
Original source code can be found here: https://github.com/delventhalz/transfer-chain-js/blob/master/processor/index.js
 */

"use strict";
const program = require("commander");
const { TransactionProcessor } = require("sawtooth-sdk/processor");
const { JSONHandler } = require("./handlers");

program
  .version("0.1.0")
  .option(
    "-C, --connect []",
    "Validator Url",
    "tcp://localhost:" + process.env.PORT || 34004
  )
  .parse(process.argv);

// Initialize Transaction Processor
const tp = new TransactionProcessor(program.connect);
tp.addHandler(new JSONHandler());
tp.start();
