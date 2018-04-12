# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import time

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing.secp256k1 import Secp256k1PublicKey


# try to commit something
KEY1_PRIV_HEX = \
    "2f1e7b7a130d7ba9da0068b3bb0ba1d79e7e77110302c9f746c3c2a63fe40088"
KEY1_PUB_HEX = \
    "026a2c795a9776f75464aa3bda3534c3154a6e91b357b1181d3f515110f84b67c5"

KEY2_PRIV_HEX = \
    "51b845c2cdde22fe646148f0b51eaf5feec8c82ee921d5e0cbe7619f3bb9c62d"
KEY2_PUB_HEX = \
    "039c20a66b4ec7995391dbec1d8bb0e2c6e6fd63cd259ed5b877cb4ea98858cf6d"

MSG1 = "test"
MSG1_KEY1_SIG = ("5195115d9be2547b720ee74c23dd841842875db6eae1f5da8605b050a49e"
                 "702b4aa83be72ab7e3cb20f17c657011b49f4c8632be2745ba4de79e6aa0"
                 "5da57b35")

MSG2 = "test2"
MSG2_KEY2_SIG = ("d589c7b1fa5f8a4c5a389de80ae9582c2f7f2a5e21bab5450b670214e5b1"
                 "c1235e9eb8102fd0ca690a8b42e2c406a682bd57f6daf6e142e5fa4b2c26"
                 "ef40a490")


# 64 us per operation, 15k ops/s
def test_hex_key(benchmark):
    priv_key = benchmark(Secp256k1PrivateKey.from_hex, KEY1_PRIV_HEX)
    assert priv_key.get_algorithm_name() == "secp256k1"
    assert priv_key.as_hex() == KEY1_PRIV_HEX

# 91 us per operation, 11k ops/s
def test_single_key_signing(benchmark):
    context = create_context("secp256k1")
    factory = CryptoFactory(context)
    priv_key = Secp256k1PrivateKey.from_hex(KEY1_PRIV_HEX)    
    signer = factory.new_signer(priv_key)
    signature = benchmark(signer.sign, MSG1.encode())
    
    assert signature == MSG1_KEY1_SIG

# 77 us per operation, 13k ops/s
def test_verification(benchmark):
    context = create_context("secp256k1")
    factory = CryptoFactory(context)
    pub_key1 = Secp256k1PublicKey.from_hex(KEY1_PUB_HEX)
    result = benchmark(context.verify, MSG1_KEY1_SIG, MSG1.encode(), pub_key1)
    assert result == True

