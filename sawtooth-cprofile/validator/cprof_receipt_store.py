import cProfile
import unittest
from unittest.mock import Mock
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


def test_receipt_store_get_and_set():
    """Tests that we correctly get and set state changes to a ReceiptStore.

    This test sets a list of receipts and then gets them back,
    ensuring that the data is the same.
    """
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


def test_get_receipts():
    """Tests that the TransactionReceiptGetRequestHandler will return a
    response with the receipt for the transaction requested.
    """

    receipt_store = TransactionReceiptStore(DictDatabase())

    receipt = TransactionReceipt(
        data=["beef".encode()])

    receipt_store.put("deadbeef", receipt)

    handler = ClientReceiptGetRequestHandler(receipt_store)

    request = ClientReceiptGetRequest(
        transaction_ids=['deadbeef']).SerializeToString()

    response = handler.handle('test_conn_id', request)

    request = ClientReceiptGetRequest(
        transaction_ids=['unknown']).SerializeToString()

    response = handler.handle('test_conn_id', request)


def test_add_event():
    mock_add_receipt_data = Mock()
    handler = TpReceiptAddDataHandler(mock_add_receipt_data)
    request = TpReceiptAddDataRequest().SerializeToString()

    response = handler.handle("test_conn_id", request)


if __name__ == '__main__':
    print("\n====== cProfile: receipt_store.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_receipt_store_get_and_set()
    test_get_receipts()
    test_add_event()

    pr.disable()
    pr.print_stats(sort='time')
