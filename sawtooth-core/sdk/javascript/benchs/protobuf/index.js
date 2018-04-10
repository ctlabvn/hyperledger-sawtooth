const Benchmark = require('benchmark');
const { Message } = require('../../protobuf/index');
const { exportToFile } = require('../../utils');

var suite = new Benchmark.Suite();
var results = [];
var testEncodeMessage = Message.encode({
  messageType: Message.MessageType.CLIENT_STATE_GET_REQUEST,
  correlationId: 'corr_id',
  content: Buffer.from('Hello', 'utf8')
}).finish();

suite
  .add('test_encode_messages', function() {
    let encMessage = Message.encode({
      messageType: Message.MessageType.CLIENT_STATE_GET_REQUEST,
      correlationId: 'corr_id',
      content: Buffer.from('Hello', 'utf8')
    }).finish();
  })
  .add('test_decode_messages', function() {
    let decMessage = Message.decode(testEncodeMessage);
  })
  .on('cycle', function(event) {
    var jsonEvent = JSON.parse(JSON.stringify(event.target));
    results.push({
      name: jsonEvent.name,
      ops: jsonEvent.hz ? jsonEvent.hz.toFixed(jsonEvent.hz < 100 ? 2 : 0) : 0,
      cycles: jsonEvent.stats.sample.length,
      [`tpo(μs)`]: jsonEvent.hz ? (1 / jsonEvent.hz * 1000000).toFixed(2) : 0
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
    exportToFile('protobuf_test', finalResult);
  })
  .run({ async: true });
