##Benchmark Hyperledger Sawtooth

## Run testcases:

```bash
python -m unittest consensus/poet/common/tests/test_sgx_structs/test_hello.py
```

## Run benchmark

Required `pip install pytest-benchmark`

```bash
pytest consensus/poet/common/tests/test_sgx_structs/bench_hello.py
```
