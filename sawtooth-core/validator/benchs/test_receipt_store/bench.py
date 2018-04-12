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

import unittest
from unittest.mock import Mock
import pytest
from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.execution.tp_state_handlers import \
    TpReceiptAddDataHandler
from sawtooth_validator.journal.receipt_store import TransactionReceiptStore
from sawtooth_validator.journal.receipt_store import \
    ClientReceiptGetRequestHandler

from sawtooth_validator.networking.dispatch import HandlerStatus

from sawtooth_validator.protobuf.transaction_receipt_pb2 import \
    TransactionReceipt
from sawtooth_validator.protobuf.transaction_receipt_pb2 import StateChange
from sawtooth_validator.protobuf.client_receipt_pb2 import \
    ClientReceiptGetRequest
from sawtooth_validator.protobuf.client_receipt_pb2 import \
    ClientReceiptGetResponse
from sawtooth_validator.protobuf.events_pb2 import Event
from sawtooth_validator.protobuf.state_context_pb2 import \
    TpReceiptAddDataRequest



def test_receipt_store_get_and_set(benchmark):
    """Tests that we correctly get and set state changes to a ReceiptStore.

    This test sets a list of receipts and then gets them back,
    ensuring that the data is the same.
    """
    @benchmark
    def do_receipt_store_get_and_set():
        receipt_store = TransactionReceiptStore(DictDatabase())

        receipts = []
        for i in range(10):
            state_changes = []
            events = []
            data = []

            for j in range(10):
                string = str(j)
                byte = string.encode()

                state_changes.append(
                    StateChange(
                        address='a100000' + string,
                        value=byte,
                        type=StateChange.SET))
                events.append(
                    Event(
                        event_type="test",
                        data=byte,
                        attributes=[Event.Attribute(key=string,
                                                    value=string)]))
                data.append(byte)

            receipts.append(
                TransactionReceipt(
                    state_changes=state_changes, events=events, data=data))

        for i, receipt in enumerate(receipts):
            receipt_store.put(str(i), receipt)

        for i, receipt in enumerate(receipts):
            stored_receipt = receipt_store.get(str(i))

            assert stored_receipt.state_changes == receipt.state_changes
            


def test_raise_key_error_on_missing_receipt(benchmark):
    """Tests that we correctly raise key error on a missing receipt
    """
    @benchmark
    def do_raise_key_error_on_missing_receipt():
        receipt_store = TransactionReceiptStore(DictDatabase())

        with pytest.raises(KeyError):
            receipt_store.get('unknown')



def test_get_receipts(benchmark):
    """Tests that the TransactionReceiptGetRequestHandler will return a
    response with the receipt for the transaction requested.
    """
    @benchmark
    def do_get_receipts():
        receipt_store = TransactionReceiptStore(DictDatabase())

        receipt = TransactionReceipt(
            data=["beef".encode()])

        receipt_store.put("deadbeef", receipt)

        handler = ClientReceiptGetRequestHandler(receipt_store)

        request = ClientReceiptGetRequest(
            transaction_ids=['deadbeef']).SerializeToString()

        response = handler.handle('test_conn_id', request)
        assert HandlerStatus.RETURN == response.status        
        
        request = ClientReceiptGetRequest(
            transaction_ids=['unknown']).SerializeToString()

        response = handler.handle('test_conn_id', request)
        assert HandlerStatus.RETURN == response.status        



def test_add_event(benchmark):
    @benchmark
    def do_add_event():
        mock_add_receipt_data = Mock()
        handler = TpReceiptAddDataHandler(mock_add_receipt_data)
        request = TpReceiptAddDataRequest().SerializeToString()

        response = handler.handle("test_conn_id", request)

        assert HandlerStatus.RETURN == response.status
