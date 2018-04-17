const test = require("tape");
const Cargo = require("../lib/cargo");

test("Cargo test", function(t) {
  const cargo = new Cargo(
    (tasks, callback) => {
      // the tasks array will be [1, 2, 3]
      console.log(tasks);
      // this will be called after 1000ms, as number of items (3) is smaller than payload (10)
      callback("err", "arg");
    },
    10,
    1000
  );

  cargo.push(1);
  cargo.push(2);

  cargo.push(3, (err, arg) => {
    console.log(err, arg);
  });

  for (let i = 4; i < 20; i++) {
    cargo.push(i);
  }

  t.end();
});
