var Benchmark = require('benchmark');
var Deferred = require('../../messaging/deferred');

var suite = new Benchmark.Suite();
// describe('Test Messaging', () => {
//   // Create new userInformation, role: Admin
//   it('Test Deferred ', () => {
//     Deferred();
//     // expect(state.type).toEqual(TypesActions.POST_USER_INFORMATION_REQUEST);
//   });
// });

suite
  .add('Deferred', function() {
    Deferred();
  })
  .on('cycle', function(event) {
    console.log(String(event.target));
  })
  .on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').map('name'));
  })
  .run({ async: true });
