# Copyright 2017 Intel Corporation
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

import json
import base64
import hashlib
import os
import unittest

from sawtooth_processor_test.mock_validator import MockValidator
from validator_reg_message_factory import ValidatorRegistryMessageFactory

from sawtooth_poet_common import sgx_structs
from sawtooth_poet_common.protobuf.validator_registry_pb2 import \
    ValidatorRegistryPayload

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


PRIVATE = '2f1e7b7a130d7ba9da0068b3bb0ba1d79e7e77110302c9f746c3c2a63fe40088'


class TestValidatorRegistry():

    
    def __init__(self):
        url = os.getenv('TEST_BIND', 'tcp://127.0.0.1:4004')

        self.validator = MockValidator()

        self.validator.listen(url)

        if not self.validator.register_processor():
            raise Exception('Failed to register processor')

        self.factory = None

    
    def __exit__(self):
        try:
            self.validator.close()
        except AttributeError:
            pass

    
    def __enter__(self):
        context = create_context('secp256k1')
        private_key = Secp256k1PrivateKey.from_hex(PRIVATE)
        signer = CryptoFactory(context).new_signer(private_key)

        self.factory = ValidatorRegistryMessageFactory(
            signer=signer)

    def _expect_invalid_transaction(self):
        self.validator.expect(
            self.factory.create_tp_response("INVALID_TRANSACTION"))

    def _expect_ok(self):
        self.validator.expect(self.factory.create_tp_response("OK"))

    def _test_valid_signup_info(self, signup_info):
        """
        Testing valid validator_registry transaction.
        """
        payload = ValidatorRegistryPayload(
            verb="reg", name="val_1", id=self.factory.public_key,
            signup_info=signup_info)
        # Send validator registry payload
        transaction_message =\
            self.factory.create_tp_process_request(payload.id, payload)
        transaction_id = transaction_message.signature
        self.validator.send(
            transaction_message)

        # Expect Request for the address for report key PEM
        received = self.validator.expect(
            self.factory.create_get_request_report_key_pem())

        # Respond with simulator report key PEM
        self.validator.respond(
            self.factory.create_get_response_simulator_report_key_pem(),
            received)

        # Expect Request for the address for valid enclave measurements
        received = self.validator.expect(
            self.factory.create_get_request_enclave_measurements())

        # Respond with the simulator valid enclave measurements
        self.validator.respond(
            self.factory.create_get_response_simulator_enclave_measurements(),
            received)

        # Expect Request for the address for valid enclave basenames
        received = self.validator.expect(
            self.factory.create_get_request_enclave_basenames())

        # Respond with the simulator valid enclave basenames
        self.validator.respond(
            self.factory.create_get_response_simulator_enclave_basenames(),
            received)

        # Expect Request for the ValidatorMap
        received = self.validator.expect(
            self.factory.create_get_request_validator_map())

        # Respond with a empty validator Map
        self.validator.respond(
            self.factory.create_get_empty_response_validator_map(), received)

        # Expect a set the new validator to the ValidatorMap
        received = self.validator.expect(
            self.factory.create_set_request_validator_map())

        # Respond with the ValidatorMap address
        self.validator.respond(
            self.factory.create_set_response_validator_map(),
            received)

        # Expect a request to set ValidatorInfo for val_1
        received = self.validator.expect(
            self.factory.create_set_request_validator_info(
                "val_1", transaction_id, signup_info))

        # Respond with address for val_1
        # val_1 address is derived from the validators id
        # val id is the same as the public_key for the factory
        self.validator.respond(
            self.factory.create_set_response_validator_info(),
            received)

        self._expect_ok()


    def _test_bad_signup_info(self, signup_info, expect_config=True):
        payload = ValidatorRegistryPayload(
            verb="reg",
            name="val_1",
            id=self.factory.public_key,
            signup_info=signup_info)

        # Send validator registry payload
        self.validator.send(
            self.factory.create_tp_process_request(payload.id, payload))

        if expect_config:
            # Expect Request for the address for report key PEM
            received = self.validator.expect(
                self.factory.create_get_request_report_key_pem())

            # Respond with simulator report key PEM
            self.validator.respond(
                self.factory.create_get_response_simulator_report_key_pem(),
                received)

            # Expect Request for the address for valid enclave measurements
            received = self.validator.expect(
                self.factory.create_get_request_enclave_measurements())

            # Respond with the simulator valid enclave measurements
            self.validator.respond(
                self.factory.
                create_get_response_simulator_enclave_measurements(),
                received)

            # Expect Request for the address for valid enclave basenames
            received = self.validator.expect(
                self.factory.create_get_request_enclave_basenames())

            # Respond with the simulator valid enclave basenames
            self.validator.respond(
                self.factory.create_get_response_simulator_enclave_basenames(),
                received)

        self._expect_invalid_transaction()


def test_valid_signup_info(benchmark):
    
    with TestValidatorRegistry() as testValidatorRegistry:
        signup_info = benchmark(testValidatorRegistry.factory.create_signup_info,
            testValidatorRegistry.factory.public_key_hash, "000")

        testValidatorRegistry._test_valid_signup_info(signup_info)

        # Re-register the same validator. Expect success.
        testValidatorRegistry._test_valid_signup_info(signup_info)

def test_out_of_date_tcb(benchmark):
    with TestValidatorRegistry() as testValidatorRegistry:
        signup_info = benchmark(testValidatorRegistry.factory.create_signup_info,
            testValidatorRegistry.factory.public_key_hash, "000", "OUT_OF_DATE")
        testValidatorRegistry._test_valid_signup_info(signup_info)

def test_invalid_name(benchmark):
    """
    Test that a transaction with an invalid name returns an invalid
    transaction.
    """
    @benchmark
    def do_invalid_name():        
        with TestValidatorRegistry() as testValidatorRegistry:

            signup_info = testValidatorRegistry.factory.create_signup_info(
                testValidatorRegistry.factory.public_key_hash, "000")

            # The name is longer the 64 characters
            payload = ValidatorRegistryPayload(
                verb="reg",
                name="val_11111111111111111111111111111111111111111111111111111111"
                     "11111",
                id=testValidatorRegistry.factory.public_key,
                signup_info=signup_info)

            # Send validator registry payload
            testValidatorRegistry.validator.send(
                testValidatorRegistry.factory.create_tp_process_request(payload.id, payload))

            testValidatorRegistry._expect_invalid_transaction()

def test_invalid_id(benchmark):
    """
    Test that a transaction with an id that does not match the
    signer_public_key returns an invalid transaction.
    """

    @benchmark
    def do_invalid_id():  
        with TestValidatorRegistry() as testValidatorRegistry:
            signup_info = testValidatorRegistry.factory.create_signup_info(
                testValidatorRegistry.factory.public_key_hash, "000")

            # The idea should match the signer_public_key in the transaction_header
            payload = ValidatorRegistryPayload(
                verb="reg",
                name="val_1",
                id="bad",
                signup_info=signup_info
            )

            # Send validator registry payload
            testValidatorRegistry.validator.send(
                testValidatorRegistry.factory.create_tp_process_request(payload.id, payload))

            testValidatorRegistry._expect_invalid_transaction()

