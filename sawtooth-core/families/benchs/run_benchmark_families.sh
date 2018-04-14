#!/bin/bash

benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/families_blockinfo_sawtoothblockinfo.json ./bench_block_info/families_blockinfo_sawtoothblockinfo.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/families_blockinfo_sawtoothblockinfo_processor.json ./bench_block_info/families_blockinfo_sawtoothblockinfo_processor.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/families_identity_sawtoothidentity_processor.json ./bench_identity/families_identity_sawtoothidentity_processor.py




find . -type d -name __pycache__ -exec rm -r {} \+
rm -Rf ./.benchmarks
find . -type d -name .cache -exec rm -r {} \+