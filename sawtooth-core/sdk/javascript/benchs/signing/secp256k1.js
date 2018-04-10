const Benchmark = require('benchmark');
const { createContext, CryptoFactory, ParseError } = require('../../signing');
const {
  Secp256k1PrivateKey,
  Secp256k1PublicKey
} = require('../../signing/secp256k1');
const { exportToFile } = require('../../utils');

var suite = new Benchmark.Suite();
var results = [];

const KEY1_PRIV_HEX =
  '2f1e7b7a130d7ba9da0068b3bb0ba1d79e7e77110302c9f746c3c2a63fe40088';
const KEY1_PUB_HEX =
  '026a2c795a9776f75464aa3bda3534c3154a6e91b357b1181d3f515110f84b67c5';

const KEY2_PRIV_HEX =
  '51b845c2cdde22fe646148f0b51eaf5feec8c82ee921d5e0cbe7619f3bb9c62d';
const KEY2_PUB_HEX =
  '039c20a66b4ec7995391dbec1d8bb0e2c6e6fd63cd259ed5b877cb4ea98858cf6d';

const MSG1 = 'test';
const MSG1_KEY1_SIG =
  '5195115d9be2547b720ee74c23dd841842875db6eae1f5da8605b050a49e' +
  '702b4aa83be72ab7e3cb20f17c657011b49f4c8632be2745ba4de79e6aa0' +
  '5da57b35';

const MSG2 = 'test2';
const MSG2_KEY2_SIG =
  'd589c7b1fa5f8a4c5a389de80ae9582c2f7f2a5e21bab5450b670214e5b1' +
  'c1235e9eb8102fd0ca690a8b42e2c406a682bd57f6daf6e142e5fa4b2c26' +
  'ef40a490';

const privTestKey1 = Secp256k1PrivateKey.fromHex(KEY1_PRIV_HEX);
const pubKey1 = Secp256k1PublicKey.fromHex(KEY1_PUB_HEX);

suite
  .add('test_parsing', function() {
    Secp256k1PrivateKey.fromHex(KEY1_PRIV_HEX);
  })
  .add('test_private to public', function() {
    let context = createContext('secp256k1');

    context.getPublicKey(privTestKey1);
  })
  .add('test_single_signing', function() {
    let context = createContext('secp256k1');
    let factory = new CryptoFactory(context);
    let signer = factory.newSigner(privTestKey1);
    let signature = signer.sign(Buffer.from(MSG1));
  })
  .add('test_multiple_signing', function() {
    let context = createContext('secp256k1');
    let signature = context.sign(Buffer.from(MSG1), privTestKey1);
  })
  .add('test_verification', function() {
    let context = createContext('secp256k1');

    let result = context.verify(MSG1_KEY1_SIG, Buffer.from(MSG1), pubKey1);
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
    exportToFile('signing_test', finalResult);
  })
  .run({ async: true });
