#!/bin/bash

benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_admin_cmd.json bench_cli_admin_cmd.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_main.json bench_cli_main.py
wait
benchs --benchmark-autosave --benchmark-enable --benchmark-verbose --benchmark-json=/project/result/bench_cli_network_cmd.json bench_cli_network_cmd.py