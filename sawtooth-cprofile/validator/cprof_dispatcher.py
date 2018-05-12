import cProfile

from concurrent.futures import ThreadPoolExecutor
from sawtooth_validator.networking import dispatch
from sawtooth_validator.protobuf import validator_pb2

from test_dispatcher.mock import MockSendMessage
from test_dispatcher.mock import MockHandler1
from test_dispatcher.mock import MockHandler2


_connection = "TestConnection"
_dispatcher = dispatch.Dispatcher()
thread_pool = ThreadPoolExecutor()

_dispatcher.add_handler(
    validator_pb2.Message.DEFAULT,
    MockHandler1(),
    thread_pool)
_dispatcher.add_handler(
    validator_pb2.Message.DEFAULT,
    MockHandler2(),
    thread_pool)
_message_ids = [str(i) for i in range(10)]
_identities = [str(i) for i in range(10)]
_connections = {chr(int(x) + 65): x for x in _identities}
mock_send_message = MockSendMessage(_connections)
_dispatcher.add_send_message(_connection, mock_send_message.send_message)
_messages = [
    validator_pb2.Message(
        content=validator_pb2.Message(
            correlation_id=m_id).SerializeToString(),
        message_type=validator_pb2.Message.DEFAULT)
    for m_id in _message_ids
]

if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_dispatcher.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    _dispatcher.start()
    for connection_id, message in zip(_connections, _messages):
        _dispatcher.dispatch(_connection, message, connection_id)
    _dispatcher.block_until_complete()
    
    pr.disable()
    pr.print_stats(sort='time')
