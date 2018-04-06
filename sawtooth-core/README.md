##Benchmark Hyperledger Sawtooth

Add running packages to the environment:

```bash
# cd validator
python setup.py install
export PYTHONPATH=$PYTHONPATH:\
          $PWD/validator:\
          $PWD/signing:\
          $PWD/consensus/poet/common:\
          $PWD/consensus/poet/core:\
          $PWD/consensus/poet/core/tests:\
          $PWD/consensus/poet/simulator
```

## Run testcases:

```bash
python -m unittest consensus/poet/common/tests/test_sgx_structs/test_hello.py
```

## Run benchmark

Required `pip install pytest-benchmark`

```bash
pytest consensus/poet/common/tests/test_sgx_structs/bench_hello.py
```

## Build protobuf template into python class:

```bash
protoc -I=consensus/poet/families/sawtooth_validator_registry/protos --python_out=consensus/poet/common/sawtooth_poet_common/protobuf consensus/poet/families/sawtooth_validator_registry/protos/validator_registry.proto
```
