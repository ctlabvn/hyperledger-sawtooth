#!/bin/bash
python3 ./poet/common/cprof_sgx_struct.py
wait
python3 ./poet/core/cprof_consensus_state_store.py
wait
python3 ./poet/core/cprof_consensus_sate.py