const express = require('express');
const app = express();
const bodyParser = require('body-parser');

var BlockChain = require('./blockchain.js');

// var childProcess = require("child_process")
// var exec = childProcess.exec
// var path = require("path")
// var tape = require("tape")
// var _test = require("tape-promise")
// var test = _test(tape)
// var table = require("table")
// var Monitor = require("./monitor.js")
// var Report = require("./report.js")
// var Client = require("./client/client.js")

// var blockchain, monitor, report, client

// var resultsbyround = []
// var round = 0
// var demo = require("../gui/src/demo.js")

// var absCaliperDir = path.join(__dirname, "../..")

// // set outputFolder and format
// var outputFolder
// var outputFormat

var blockchain;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', (req, res) => res.send('Hello World!'));

app.post('/invokeSmartContract', function(req, res) {
  console.log(req.body.key);
  res.send('POST invokeSmartContract request received');

  let context = undefined;
  let contractID = 'simple';
  let contractVer = '1.0';
  let date = new Date();
  let args = {
    verb: 'open',
    account: date.getTime() + '',
    money: '10000'
  };
  let timeout = 30;

  return blockchain.invokeSmartContract(
    context,
    contractID,
    contractVer,
    args,
    timeout
  );
});

app.listen(3000, function() {
  var network = {
    sawtooth: {
      network: {
        restapi: {
          url: 'http://192.168.1.159:30080'
        }
      }
    },
    file:
      '/Users/macbook/Documents/work/AgileTech/sawtooth-core-benchmark/sawtooth-caliper/benchmark/simple/sawtooth.json'
  };

  blockchain = new BlockChain(network);
});

// function createReport(config, sut) {
//     report = new Report();
//     report.addMetadata("DLT", blockchain.gettype());
//     try {
//         report.addMetadata("Benchmark", config.test.name);
//     } catch (err) {
//         report.addMetadata("Benchmark", " ");
//     }
//     try {
//         report.addMetadata("Description", config.test.description);
//     } catch (err) {
//         report.addMetadata("Description", " ");
//     }
//     try {
//         var r = 0;
//         for (let i = 0; i < config.test.rounds.length; i++) {
//             if (config.test.rounds[i].hasOwnProperty("txNumber")) {
//                 r += config.test.rounds[i].txNumber.length;
//             }
//         }
//         report.addMetadata("Test Rounds", r);

//         report.setBenchmarkInfo(JSON.stringify(config.test, null, 2));
//     } catch (err) {
//         report.addMetadata("Test Rounds", " ");
//     }

//     if (sut.hasOwnProperty("info")) {
//         for (let key in sut.info) {
//             report.addSUTInfo(key, sut.info[key]);
//         }
//     }
// }

// function defaultTest(network, args, clientArgs, final) {
// 	return new Promise(function(resolve, reject) {
// 		const t = global.tapeObj
// 		t.comment("\n\n##### testing '" + args.label + "' ######")
// 		const testLabel = args.label
// 		const testRounds = args.txDuration ? args.txDuration : args.txNumber
// 		const tests = []

// 		for (let i = 0; i < testRounds.length; i++) {
// 			let msg = {
// 				type: "test",
// 				label: args.label,
// 				rateControl: args.rateControl[i]
// 					? args.rateControl[i]
// 					: { type: "fixed-rate", opts: {tps: 1} },
// 				trim: args.trim ? args.trim : 0,
// 				args: args.arguments,
// 				cb: args.callback,
// 				config: network
// 			}

// 			if (args.txNumber) {
// 				msg.numb = testRounds[i]
// 			} else if (args.txDuration) {
// 				msg.txDuration = testRounds[i]
// 			} else {
// 				return reject(new Error("Unspecified test driving mode"))
// 			}

// 			tests.push(msg);
// 		}

// 		var testIdx = 0
// 		return tests
// 			.reduce(function(prev, item) {
// 				return prev.then(() => {
// 					console.log("----test round " + round + "----");
// 					round++;
// 					testIdx++;
// 					demo.startWatch(client)

// 					return client
// 						.startTest(item, clientArgs, processResult, testLabel)
// 						.then(() => {
// 							demo.pauseWatch()
// 							t.pass("passed '" + testLabel + "' testing")
// 							return Promise.resolve()
// 						})
// 						.then(() => {
// 							if (final && testIdx === tests.length) {
// 								return Promise.resolve()
// 							} else {
// 								console.log("wait 5 seconds for next round...")
// 								return sleep(5000).then(() => {
// 									return monitor.restart()
// 								})
// 							}
// 						})
// 						.catch(err => {
// 							demo.pauseWatch()
// 							t.fail(
// 								"failed '" +
// 									testLabel +
// 									"' testing, " +
// 									(err.stack ? err.stack : err)
// 							)
// 							return Promise.resolve()
// 						})
// 				})
// 			}, Promise.resolve())
// 			.then(() => {
// 				return resolve()
// 			})
// 			.catch(err => {
// 				t.fail(err.stack ? err.stack : err)
// 				return reject(new Error("defaultTest failed"))
// 			})
// 	})
// }

// function processResult(results, opt) {
// 	try {
// 		var resultTable = []
// 		resultTable[0] = getResultTitle()
// 		var r
// 		if (BlockChain.mergeDefaultTxStats(results) === 0) {
// 			r = BlockChain.createNullDefaultTxStats
// 			r["opt"] = opt
// 		} else {
// 			r = results[0]
// 			r["opt"] = opt
// 			resultTable[1] = getResultValue(r)

// 			if (resultsbyround.length === 0) {
// 				resultsbyround.push(resultTable[0].slice(0))
// 			}
// 			if (resultsbyround.length > 1) {
// 				resultsbyround.push(resultTable[0].slice(0))
// 			}
// 			console.log("###test result:###")
// 			printTable(resultTable)
// 			var idx = report.addBenchmarkRound(opt)
// 			report.setRoundPerformance(idx, resultTable)
// 			var resourceTable = monitor.getDefaultStats()
// 			if (resourceTable.length > 0) {
// 				console.log("### resource stats ###")
// 				printTable(resourceTable)
// 				report.setRoundResource(idx, resourceTable)
// 			}
// 			return Promise.resolve()
// 		}
// 	} catch(err) {
// 		console.log(err)
// 		return Promise.reject(err)
// 	}
// }

// function printTable(value) {
// 	var t = table.table(value, { border: table.getBorderCharacters("ramac") })
// 	console.log(t)
// }

// function getResultTitle() {
// 	return [
// 		"Name",
// 		"Succ",
// 		"Fail",
// 		"Send Rate",
// 		"Max Latency",
// 		"Min Latency",
// 		"Avg Latency",
// 		"75%ile Latency",
// 		"Throughput"
// 	]
// }

// function getResultValue(r) {
// 	var row = []

// 	try {
// 		row.push(r.opt)
// 		row.push(r.succ)
// 		row.push(r.fail)
// 		r.create.max === r.create.min
// 			? row.push(r.succ + r.fail + " tps")
// 			: row.push(
// 				((r.succ + r.fail) / (r.create.max - r.create.min)).toFixed(
// 					0
// 				) + " tps"
// 			)

// 		row.push(r.delay.max.toFixed(2) + " s")
// 		row.push(r.delay.min.toFixed(2) + " s")
// 		row.push((r.delay.sum / r.succ).toFixed(2) + " s")
// 		if (r.delay.detail.length === 0) {
// 			row.push("N/A")
// 		} else {
// 			r.delay.detail.sort(function(a, b) {
// 				return a - b
// 			})
// 			row.push(
// 				r.delay.detail[
// 					Math.floor(r.delay.detail.length * 0.75)
// 				]
// 			).toFixed(2) + " s"
// 		}

// 		r.final.max === r.final.min
// 			? row.push(r.succ + " tps")
// 			: row.push(
// 				(r.succ / (r.final.max - r.create.min)).toFixed(0) + " tps"
// 			)
// 	} catch (err) {
// 		row = [r.opt, 0, 0,  "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
// 	}

// 	return row
// }

// function printResultsByRound() {
// 	resultsbyround[0].unshift("Test")
// 	for (let i = 1; i < resultsbyround.length; i++) {
// 		resultsbyround[i].unshift(i.toFixed(0))
// 	}
// 	console.log("###all test results:###")
// 	printTable(resultsbyround)

// 	report.setSummaryTable(resultsbyround)
// }

// function sleep(ms) {
// 	return new Promise(resolve => setTimeout(resolve, ms))
// }

// app.listen(3000, function() {
// 	test("#######Caliper Test######", t => {
// 		global.tapeObj = t
// 		var network = {
// 			"sawtooth": {
// 				"network": {
// 					"restapi": {
// 						"url":"http://127.0.0.1:38080"
// 					}
// 				}
// 			},
// 			"file":"/Users/macbook/Documents/work/AgileTech/sawtooth-core-benchmark/sawtooth-caliper/benchmark/simple/sawtooth.json"
// 		}

// 		var config = {
// 			"blockchain": {
// 				"type": "sawtooth",
// 				"config": "benchmark/simple/sawtooth.json"
// 			},
// 			"/** command **/": {
// 				"start": "docker-compose -f network/sawtooth/simplenetwork/docker-compose.yaml up -d",
// 				"end": "docker-compose -f network/sawtooth/simplenetwork/docker-compose.yaml down;docker rm $(docker ps -aq)"
// 			},
// 			"test": {
// 				"clients": {
// 					"type": "local",
// 					"number": 1
// 				},
// 				"rounds": [
// 					{
// 						"label": "open",
// 						"txNumber": [100],
// 						"rateControl": [
// 							{
// 								"type": "fixed-rate",
// 								"opts": {"tps": 20}
// 							}
// 						],
// 						"arguments": {"money": 10000},
// 						"callback": "benchmark/simple/open.js"
// 					},
// 					{
// 						"label": "query",
// 						"txNumber": [100],
// 						"rateControl": [
// 							{
// 								"type": "fixed-rate",
// 								"opts": {"tps":100}
// 							}
// 						],
// 						"callback": "benchmark/simple/query.js"
// 					}
// 				]
// 			},
// 			"monitor": {
// 				"type": ["docker"],
// 				"docker": {
// 					"name": ["sawtooth"]
// 				},
// 				"interval": 1
// 			},
// 			"file":"/Users/macbook/Documents/work/AgileTech/sawtooth-core-benchmark/sawtooth-caliper/benchmark/simple/config.json"
// 		}

// 		blockchain = new BlockChain(network)
// 		monitor = new Monitor(config)
// 		client = new Client(config)
// 		createReport(config, network)
// 		demo.init();

// 		var startPromise = new Promise((resolve, reject) => {
// 			if (
// 				config.hasOwnProperty("command") &&
// 				config.command.hasOwnProperty("start")
// 			) {
// 				let child = exec(
// 					config.command.start,
// 					{ cwd: absCaliperDir },
// 					(err, stdout, stderr) => {
// 						if (err) {
// 							return reject(err)
// 						}
// 						return resolve()
// 					}
// 				)
// 				child.stdout.pipe(process.stdout)
// 			 	child.stderr.pipe(process.stderr)
// 			 	resolve()
// 			} else {
// 				resolve()
// 			}
// 		})

// 		startPromise
// 			.then(() => {
// 				return blockchain.init()
// 			})
// 			.then(() => {
// 				return blockchain.installSmartContract()
// 			})
// 			.then(() => {
// 				return client.init().then(number => {
// 					return blockchain.prepareClients(number)
// 				})
// 			})
// 			.then(clientArgs => {
// 				monitor
// 					.start()
// 					.then(() => {
// 						console.log("started monitor successfully")
// 					})
// 					.catch(err => {
// 						console.log(
// 							"could not start monitor, " + (err.stack ? err.stack : err)
// 						)
// 					})

// 				var allTests = config.test.rounds
// 				var testIdx = 0
// 				var testNum = allTests.length

// 				return allTests.reduce((prev, item) => {
// 					return prev.then(() => {
// 						++testIdx;
// 						return defaultTest(
// 							network,
// 							item,
// 							clientArgs,
// 							testIdx === testNum
// 						)
// 					})
// 				}, Promise.resolve())
// 			})
// 			.then(() => {
// 				console.log("----------finished test----------\n");
// 				printResultsByRound();
// 				monitor.printMaxStats();
// 				monitor.stop();
// 				let date = new Date()
// 					.toISOString()
// 					.replace(/-/g, "")
// 					.replace(/:/g, "")
// 					.substr(0, 15)

// 				let format = outputFormat || "json"
// 				let output = path.join(
// 					outputFolder || path.join(process.cwd(), "outputs"),
// 					"report" + date + "." + format
// 				)
// 				return report.generate(output, format).then(message => {
// 					demo.stopWatch(output)
// 					return Promise.resolve()
// 				})
// 			})
// 			.then(() => {
// 				client.stop()
// 				if (
// 					config.hasOwnProperty("command") &&
// 					config.command.hasOwnProperty("end")
// 				) {
// 					console.log(config.command.end)
// 					let end = exec(config.command.end, {cwd: absCaliperDir })
// 					end.stdout.pipe(process.stdout)
// 					end.stderr.pipe(process.stderr)
// 				}
// 				t.end()
// 			})
// 			.catch(err => {
// 				demo.stopWatch()
// 				console.log(
// 					"unexpected error, " + (err.stack ? err.stack : err)
// 				)
// 				if (
// 					config.hasOwnProperty("command") &&
// 					config.command.hasOwnProperty("end")
// 				) {
// 					console.log(config.command.end)
// 					let end = exec(config.command.end, {cwd: absCaliperDir})
// 					end.stdout.pipe(process.stdout)
// 					end.stderr.pipe(process.stderr)
// 				}
// 				t.end()
// 			})
// 	});
// })
