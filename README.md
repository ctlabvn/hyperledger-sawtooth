## Build images

```sh
docker build -f sawtooth-validator-optimized -t thanhtu/sawtooth-validator-optimized .
docker build -f sawtooth-dev-python -t thanhtu/sawtooth-dev-python .
docker build -f sawtooth-validator-pypy3 -t thanhtu/sawtooth-validator-pypy3 .
```

### Start environment

```sh
cd sawtooth-test
yarn start
# start env A
yarn startA
# stop env A
yarn stopA
# start env B
yarn startB
# stop env B
yarn stopB
```

### Run test & benchmark

```sh
docker exec -it sawtooth-validator bash
tests consensus/poet/common/tests
benchs consensus/poet/common/tests/test_sgx_structs/bench_hello.py --benchmark-json=/result/bench_secp256k1_signer.json
```
