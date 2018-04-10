const Benchmark = require('benchmark');
const { TransactionProcessor } = require('../../processor/index');
const { exportToFile } = require('../../utils');
const { JSONHandler } = require('./handler');
var suite = new Benchmark.Suite();
var results = [];

suite
  .add(
    'start stream',
    function() {
      const VALIDATOR_URL = 'tcp://localhost:4004';

      // Initialize Transaction Processor
      const tp = new TransactionProcessor(VALIDATOR_URL);
      tp.addHandler(new JSONHandler());
      tp.start();
    }
    // {
    //   maxTime: 2,
    //   async: false,
    //   delay: 1
    // }
  )
  .on('cycle', function(event) {
    var jsonEvent = JSON.parse(JSON.stringify(event.target));
    results.push({
      name: jsonEvent.name,
      ops: jsonEvent.hz ? jsonEvent.hz.toFixed(jsonEvent.hz < 100 ? 2 : 0) : 0,
      cycles: jsonEvent.stats.sample.length,
      [`tpo(μs)`]: jsonEvent.hz ? (1 / jsonEvent.hz * 1000000).toFixed(0) : 0
    });
    if (jsonEvent.error) {
      jsonEvent.error.name = jsonEvent.name;
      console.log(jsonEvent.error);
    }
    //console.log(String(event.target));
  })
  .on('complete', function() {
    console.log(results);
    console.log('Fastest is ' + this.filter('fastest').map('name'));
    let finalResult = {};
    finalResult.benchmarks = results;
    exportToFile('processor_index_test', finalResult);
  })
  .run({ async: true });
