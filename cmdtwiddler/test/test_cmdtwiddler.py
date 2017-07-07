import unittest
from xmlrpclib import Fault

from hypothesis import assume
from hypothesis import given
from hypothesis.strategies import text

from cmdtwiddler.cmdtwiddler import *

from supervisor_twiddler.tests.test_rpcinterface import *
from supervisor.xmlrpc import Faults as SupervisorFaults
from supervisor.xmlrpc import getFaultDescription


class TestCmdTwiddler(unittest.TestCase):
    def attrDictWithoutUnders(self, obj):
        """ Returns the __dict__ for an object with __unders__ removed """
        attrs = {}
        for k, v in obj.__dict__.items():
            if not k.startswith('__'): attrs[k] = v
        return attrs

    @given(text())
    def test_twiddle_action_refuses_anything_but_add_or_remove(self, action):
        assume(action != "add")
        assume(action != "remove")
        with self.assertRaises(AttributeError):
            twiddle_command(action, "test_group", "test_program")

    def test_handle_rpc_fault_handles_all_faults(self):
        supervisor_fault_codes = self.attrDictWithoutUnders(SupervisorFaults).values()
        for item in supervisor_fault_codes:
            fault = Fault(item, getFaultDescription(item))

            if item == 2 or item == 10:
                with self.assertRaises(SystemExit):
                    handle_rpc_fault(fault)
            else:
                with self.assertRaises(Fault):
                    handle_rpc_fault(fault)


if __name__ == '__main__':
    unittest.main()
