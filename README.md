### Start environment ###

```sh
docker-compose up -d
```

### Run test & benchmark ###

```sh
tests consensus/poet/common/tests
benchs consensus/poet/common/tests/test_sgx_structs/bench_hello.py
```