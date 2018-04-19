### Start environment

```sh
cd sawtooth-test
docker-compose up -d
```

### Run test & benchmark

```sh
docker exec -it sawtooth-validator-default bash
tests consensus/poet/common/tests
benchs consensus/poet/common/tests/test_sgx_structs/bench_hello.py --benchmark-json=/result/bench_secp256k1_signer.json
```
