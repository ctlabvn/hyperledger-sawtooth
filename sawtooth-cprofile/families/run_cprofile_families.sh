#!/bin/bash
python3 ./block_info/cprof_families_blockinfo.py
wait

python3 ./identity/cprof_families_identity.py