#!/bin/bash
python3 ./cprof_authorization_handlers.py
wait
python3 ./cprof_batch_tracker.py
wait
python3 ./cprof_block_cache.py
wait
python3 ./cprof_block_store.py
wait
python3 ./cprof_client_request_handlers.py
wait
python3 ./cprof_completer.py
