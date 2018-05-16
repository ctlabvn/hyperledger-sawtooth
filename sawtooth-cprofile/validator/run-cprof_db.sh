#!/bin/bash
python3 ./cprof_nolock_database.py
wait
python3 ./cprof_permission_verifier.py
wait
python3 ./cprof_receipt_store.py
wait
python3 ./cprof_validation_rule_enforcer.py
wait
python3 ./cprof_responder.py