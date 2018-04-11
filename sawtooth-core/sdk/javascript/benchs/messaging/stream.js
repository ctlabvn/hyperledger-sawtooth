const Benchmark = require('benchmark');
const {
  Stream,
  _encodeMessage,
  _generateId
} = require('../../messaging/stream');
const { exportToFile } = require('../../utils');

var suite = new Benchmark.Suite();
var results = [];

suite
  .add('test_generate_id', function() {
    _generateId();
  })
  .add('test_encode_message', function() {
    _encodeMessage(1234, '1234', Buffer.from('abc'));
  })
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
    exportToFile('messaging_test', finalResult);
  })
  .run({ async: true });
