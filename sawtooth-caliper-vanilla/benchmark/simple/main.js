/**
 * Copyright 2017 HUAWEI. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 */

"use strict";

const { requireJSON } = require("../../lib/json");

var configFile;
var networkFile;

function setConfig(file) {
    configFile = file;
}

function setNetwork(file) {
    networkFile = file;
}

function main() {
    var program = require("commander");
    program
        .version("0.1")
        .option(
            "-c, --config <file>",
            "config file of the benchmark, default is config.json",
            setConfig
        )
        .option(
            "-n, --network <file>",
            "config file of the blockchain system under test, if not provided, blockchain property in benchmark config is used",
            setNetwork
        )
        .option("--output-folder <folder>", "Folder where to save outputs to")
        .option("--output-format <format>", "formats of benchmark output files")
        .parse(process.argv);

    var path = require("path");
    var fs = require("fs-extra");
    var absConfigFile;
    if (typeof configFile === "undefined") {
        absConfigFile = path.join(__dirname, "config.json");
    } else {
        absConfigFile = path.join(__dirname, configFile);
    }
    if (!fs.existsSync(absConfigFile)) {
        console.log("file " + absConfigFile + " does not exist");
        return;
    }

    var absNetworkFile;
    var absCaliperDir = path.join(__dirname, "../..");
    let config, network;
    if (typeof networkFile === "undefined") {
        try {
            config = requireJSON(absConfigFile);
            config.file = absConfigFile;
            absNetworkFile = path.join(absCaliperDir, config.blockchain.config);
        } catch (err) {
            console.log("failed to find blockchain.config in " + absConfigFile);
            return;
        }
    } else {
        absNetworkFile = path.join(__dirname, networkFile);
    }

    if (!fs.existsSync(absNetworkFile)) {
        console.log("file " + absNetworkFile + " does not exist");
        return;
    } else {
        try {
            network = requireJSON(absNetworkFile);
            network.file = absNetworkFile;
        } catch (err) {
            console.log("failed to find network.config in " + absNetworkFile);
            return;
        }
    }

    let absOutputFolder;
    if (program.outputFolder) {
        absOutputFolder = path.join(__dirname, program.outputFolder);
        if (!fs.existsSync(absOutputFolder)) {
            console.log("folder " + absOutputFolder + " does not exist");
            return;
        }
    }

    // call framework with config file and network file
    var framework = require("../../src/comm/bench-flow.js");
    framework.setOutputFolder(absOutputFolder);
    framework.setOutputFormat(program.outputFormat);
    framework.run(config, network);
}

main();
