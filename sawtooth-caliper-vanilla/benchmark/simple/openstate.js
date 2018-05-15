/**
 * Copyright 2017 HUAWEI. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 */

"use strict";

module.exports.info = "opening accounts";

var accounts = [];
var initMoney;
var bc, contx;
var accountIndex = 0;
module.exports.init = function(blockchain, context, args) {
    if (!args.hasOwnProperty("money")) {
        return Promise.reject(
            new Error("simple.open - 'money' is missed in the arguments")
        );
    }

    initMoney = args.money.toString();
    bc = blockchain;
    contx = context;
    accounts = args.accounts;
    return Promise.resolve();
};

function generateAccount() {
    const acc = accounts[accountIndex];
    accountIndex++;
    if (accountIndex >= accounts.length) {
        accountIndex = 0;
    }
    return acc;
}

module.exports.run = function() {
    var newAcc = generateAccount();
    return bc.invokeSmartContract(
        contx,
        "simple",
        "1.0",
        {
            verb: "open",
            account: newAcc,
            money: Math.floor(Math.random() * 1000)
        },
        30
    );
};

module.exports.end = function(results) {
    return Promise.resolve();
};

module.exports.accounts = accounts;
