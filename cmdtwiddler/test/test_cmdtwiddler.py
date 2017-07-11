import unittest
from xmlrpclib import Fault

from hypothesis import assume
from hypothesis import given
from hypothesis.strategies import text

from cmdtwiddler.cmdtwiddler import *
from cmdtwiddler.RPCHelper import *

from supervisor_twiddler.tests.test_rpcinterface import *
from supervisor.xmlrpc import Faults as SupervisorFaults
from supervisor.xmlrpc import getFaultDescription


class TestCmdTwiddler(unittest.TestCase):
    @given(text())
    def test_twiddle_action_refuses_anything_but_add_or_remove(self, action):
        assume(action != "add")
        assume(action != "remove")
        with self.assertRaises(AttributeError):
            twiddle_command(action, "test_group", "test_program")

    def test_load_env_raises_exception_on_invalid_file(self):
        with self.assertRaises(AttributeError):
            twiddler = CMDTwiddler()
            twiddler.load_env("DefinitelY_not_existent")

    def test_load_env_can_load_file(self):
        expected = 'TEST="abcd123", TEST2=987'
        loaded = self.execute_load_env("/env_files/simple_success.env")
        self.assertEqual(expected, loaded)

    def test_load_env_removes_comments(self):
        expected = 'TEST="abcd123", TEST2=987'
        loaded = self.execute_load_env("/env_files/test_comment.env")
        self.assertEqual(expected, loaded)

    def test_special_chars_are_stripped(self):
        expected = 'TEST="abcd123", TEST2=987'
        loaded = self.execute_load_env("/env_files/test_tabs.env")
        self.assertEqual(expected, loaded)

    def execute_load_env(self, file):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        twiddler = CMDTwiddler()
        return twiddler.load_env(dir_path + file)


class RCPHelperTest(unittest.TestCase):
    def attrDictWithoutUnders(self, obj):
        """ Returns the __dict__ for an object with __unders__ removed """
        attrs = {}
        for k, v in obj.__dict__.items():
            if not k.startswith('__'): attrs[k] = v
        return attrs

    def test_handle_rpc_fault_handles_all_faults(self):
        rpc_helper = RPCHelper()
        supervisor_fault_codes = self.attrDictWithoutUnders(SupervisorFaults).values()
        for item in supervisor_fault_codes:
            fault = Fault(item, getFaultDescription(item))

            if item == 2 or item == 10:
                with self.assertRaises(SystemExit):
                    rpc_helper.handle_rpc_fault(fault)
            else:
                with self.assertRaises(Fault):
                    rpc_helper.handle_rpc_fault(fault)


if __name__ == '__main__':
    unittest.main()
