var test = require("tape");
const path = require("path");
const {
  calculateAddress,
  calculateAddresses
} = require("../lib/sawtooth/address");
const { createContext, CryptoFactory } = require("sawtooth-sdk/signing");
const { Secp256k1PrivateKey } = require("sawtooth-sdk/signing/secp256k1");
const accounts = [
  "zlscb",
  "zlscc",
  "zlscd",
  "zlsce",
  "zlscf",
  "zlscg",
  "zlsch",
  "zlsci",
  "zlscj",
  "zlsck",
  "zlscl",
  "zlscm",
  "zlscn",
  "zlsco",
  "zlscp",
  "zlscq",
  "zlscr",
  "zlscs",
  "zlsct",
  "zlscu",
  "zlscv",
  "zlscw",
  "zlscx",
  "zlscy",
  "zlscz",
  "zlscab",
  "zlscbb",
  "zlsccb",
  "zlscdb",
  "zlsceb",
  "zlscfb",
  "zlscgb",
  "zlschb",
  "zlscib",
  "zlscjb",
  "zlsckb",
  "zlsclb",
  "zlscmb",
  "zlscnb",
  "zlscob",
  "zlscpb",
  "zlscqb",
  "zlscrb",
  "zlscsb",
  "zlsctb",
  "zlscub",
  "zlscvb",
  "zlscwb",
  "zlscxb",
  "zlscyb",
  "zlsczb",
  "zlscac",
  "zlscbc",
  "zlsccc",
  "zlscdc",
  "zlscec",
  "zlscfc",
  "zlscgc",
  "zlschc",
  "zlscic",
  "zlscjc",
  "zlsckc",
  "zlsclc",
  "zlscmc",
  "zlscnc",
  "zlscoc",
  "zlscpc",
  "zlscqc",
  "zlscrc",
  "zlscsc",
  "zlsctc",
  "zlscuc",
  "zlscvc",
  "zlscwc",
  "zlscxc",
  "zlscyc",
  "zlsczc",
  "zlscad",
  "zlscbd",
  "zlsccd",
  "zlscdd",
  "zlsced",
  "zlscfd",
  "zlscgd",
  "zlschd",
  "zlscid",
  "zlscjd",
  "zlsckd",
  "zlscld",
  "zlscmd",
  "zlscnd",
  "zlscod",
  "zlscpd",
  "zlscqd",
  "zlscrd",
  "zlscsd",
  "zlsctd",
  "zlscud",
  "zlscvd",
  "zlscwd"
];

test("address test", function(t) {
  var acc = accounts[Math.floor(Math.random() * accounts.length)];
  const address = calculateAddress("simple", acc);
  console.log(address);
  t.end();
});

test("secp256k1 test", function(t) {
  const cryptoContext = createContext("secp256k1");
  const privateKey = cryptoContext.newRandomPrivateKey();
  const stringKey = privateKey.asBytes().toString("hex");
  console.log(stringKey);
  const retrieveKey = Secp256k1PrivateKey.fromHex(stringKey);
  t.equal(stringKey, retrieveKey.asBytes().toString("hex"));
  t.end();
});
