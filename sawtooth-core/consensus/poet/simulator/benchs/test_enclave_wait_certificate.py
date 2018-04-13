# Copyright 2016, 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import unittest

from sawtooth_signing import create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_poet_simulator.poet_enclave_simulator.enclave_wait_timer \
    import EnclaveWaitTimer
from sawtooth_poet_simulator.poet_enclave_simulator.enclave_wait_certificate \
    import EnclaveWaitCertificate



def _create_random_key():
    return Secp256k1PrivateKey.new_random()

def test_create_wait_certificate(benchmark):
    @benchmark
    def do_create_wait_certificate():
        wait_timer = \
            EnclaveWaitTimer(
                validator_address='1600 Pennsylvania Avenue NW',
                duration=3.14159,
                previous_certificate_id='Smart, Maxwell Smart',
                local_mean=2.71828)

        wait_certificate = \
            EnclaveWaitCertificate.wait_certificate_with_wait_timer(
                wait_timer=wait_timer,
                nonce='Eeny, meeny, miny, moe.',
                block_hash='Indigestion. Pepto Bismol.')
        

        # You probably wonder why I bother assigning
        # wait_certificate.previous_certificate_id  to a local variable -
        # this is to simply get around PEP8.
        # If I don't, it complains about the line being too long.
        # If I do a line continuation, it complains about a space around the =.
        previous_certificate_id = wait_certificate.previous_certificate_id
        other_wait_certificate = \
            EnclaveWaitCertificate(
                duration=wait_certificate.duration,
                previous_certificate_id=previous_certificate_id,
                local_mean=wait_certificate.local_mean,
                request_time=wait_certificate.request_time,
                validator_address='1600 Pennsylvania Avenue NW',
                nonce='Eeny, meeny, miny, moe.',
                block_hash=wait_certificate.block_hash)


def test_serialize_wait_certificate(benchmark):
    @benchmark
    def do_serialize_wait_certificate():
        wait_timer = \
            EnclaveWaitTimer(
                validator_address='1600 Pennsylvania Avenue NW',
                duration=3.14159,
                previous_certificate_id='Smart, Maxwell Smart',
                local_mean=2.71828)

        wait_certificate = \
            EnclaveWaitCertificate.wait_certificate_with_wait_timer(
                wait_timer=wait_timer,
                nonce='Eeny, meeny, miny, moe.',
                block_hash='Indigestion. Pepto Bismol.')

    

def test_deserialized_wait_certificate(benchmark):
    @benchmark
    def do_deserialized_wait_certificate():
        wait_timer = \
            EnclaveWaitTimer(
                validator_address='1600 Pennsylvania Avenue NW',
                duration=3.14159,
                previous_certificate_id='Smart, Maxwell Smart',
                local_mean=2.71828)

        wait_certificate = \
            EnclaveWaitCertificate.wait_certificate_with_wait_timer(
                wait_timer=wait_timer,
                nonce='Eeny, meeny, miny, moe.',
                block_hash='Indigestion. Pepto Bismol.')

        serialized = wait_certificate.serialize()
        private_key = _create_random_key()
        wait_certificate.signature = \
            create_context('secp256k1').sign(serialized.encode(), private_key)

        copy_wait_certificate = \
            EnclaveWaitCertificate.wait_certificate_from_serialized(
                serialized,
                wait_certificate.signature)

