#!/bin/bash
python3 ./ias_client/cprof_ias_client.py
wait
python3 ./ias_proxy/cprof_ias_proxy.py