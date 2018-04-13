#!/bin/bash

benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_block_info_common.json bench_block_info_common.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_block_info_processor.json bench_block_info_processor.py