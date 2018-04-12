#!/bin/bash

benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_admincmd_keygen.json ./admin_cmd/bench_cli_admincmd_keygen.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_admincmd_genesis.json ./admin_cmd/bench_cli_admincmd_genesis.py
wait


benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_common_main.json ./commons/bench_cli_common_main.py
wait


benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_network_cmd_compare.json ./network_cmd/bench_cli_networkcmd_compare.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_network_cmd_peers.json ./network_cmd/bench_cli_networkcmd_peers.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_networkcmd_listblocks.json ./network_cmd/bench_cli_networkcmd_listblocks.py
wait


find . -type d -name __pycache__ -exec rm -r {} \+
rm -Rf ./.benchmarks
