## Most time consuming functions
### consensus
* validator_did_claim_block
---
### families
* load_block_info_config
---
### signing
* Secp256k1PrivateKey.from_hex
* Secp256k1PublicKey.from_hex
---
### validator
* Create connection request with Authorization (do_connect)
* Create/Get block info
* Block caching
---
### utility
* connectionpool.py:437(urlopen) belong to [urllib3](https://urllib3.readthedocs.io/en/latest/) * mbcsgroupprober.py:30(<module>) belong to [loglex](https://github.com/heroku/logplex) * adapters.py:329(send) belong to [requests](https://github.com/requests/requests/blob/master/requests/adapters.py) * module sawtooth_ias_client.ias_client -> method post_verify_attestation()