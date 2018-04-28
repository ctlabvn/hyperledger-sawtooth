import cProfile

from sawtooth_identity.processor.handler import _setting_key_to_address
from sawtooth_identity.processor.handler import _get_role_address
from sawtooth_identity.processor.handler import _get_policy_address
from sawtooth_processor_test.mock_validator import MockValidator
from sawtooth_identity.processor.main import setup_loggers
from sawtooth_identity.processor.main import create_console_handler
from sawtooth_identity.processor.main import load_identity_config
from sawtooth_identity.processor.main import create_parser
from sawtooth_identity.processor.main import create_identity_config

#########################################################################################
TEST_KEY = "aaaaaa.bbbbbb.cccccccc"

#########################################################################################

def do_setting_key_to_address():
    _setting_key_to_address(key=TEST_KEY)

def do_get_role_address():
    _get_role_address(role_name=TEST_KEY)


if __name__ == '__main__':
    print("\n====== cProfile: ./families/identity/cprof_families_identity.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_setting_key_to_address()
    do_get_role_address()

    pr.disable()
    pr.print_stats(sort='time')