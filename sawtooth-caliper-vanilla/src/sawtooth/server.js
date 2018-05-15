const express = require("express"); // call express
const bodyParser = require("body-parser"); // in express

const Sawtooth = require("./sawtooth.js");
const config = require("../../benchmark/simple/sawtooth.json");

const sawtooth = new Sawtooth(config);

const app = express();
const context = null;
const contractID = "simple";
const contractVer = "1.0";

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.get("/open", (req, res) => {
  const args = {
    verb: req.query.action,
    money: req.query.asset,
    account: req.query.owner
  };
  sawtooth
    .invokeSmartContract(context, contractID, contractVer, args, 120)
    .then(ret => {
      res.send(ret);
    });
});

app.get("/query", (req, res) => {
  const key = req.query.key;
  sawtooth.queryState(context, contractID, contractVer, key).then(ret => {
    res.send(ret);
  });
});

// Save our port
const port = process.env.PORT || 9000;

// Start the server and listen on port
app.listen(port, "0.0.0.0", () => {
  console.log("Live on port: " + port);
});
