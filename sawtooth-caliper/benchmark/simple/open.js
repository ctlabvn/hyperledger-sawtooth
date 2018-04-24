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
module.exports.init = function(blockchain, context, args) {
    // if (!args.hasOwnProperty("money")) {
    //     return Promise.reject(
    //         new Error("simple.open - 'money' is missed in the arguments")
    //     );
    // }

    initMoney = args.money;
    bc = blockchain;
    contx = context;
    return Promise.resolve();
};

var dic = "abcdefghijklmnopqrstuvwxyz";
function get26Num(number) {
    var result = "";
    while (number > 0) {
        result += dic.charAt(number % 26);
        number = parseInt(number / 26);
    }
    return result;
}
var prefix;
function generateAccount() {
    // should be [a-z]{1,9}
    if (typeof prefix === "undefined") {
        const number = process.pid;
        prefix = get26Num(number);
    }
    return prefix + get26Num(accounts.length + 1);
}

module.exports.run = function() {
    var newAcc = generateAccount();
    accounts.push(newAcc);
    return bc.invokeSmartContract(
        contx,
        "simple",
        "1.0",
        {
            verb: "open",
            account: newAcc,
            money: initMoney || Math.floor(Math.random() * 1000)
        },
        30
    );
};

module.exports.end = function(results) {
    return Promise.resolve();
};

module.exports.accounts = accounts;
