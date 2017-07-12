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

from cmdtwiddler.supervisor_conf_file_parser import SupervisorConfigParser, ParseError


class TestConfigParser(unittest.TestCase):
    def test_load_config_raises_exception_on_invalid_file(self):
        with self.assertRaises(AttributeError):
            parser = SupervisorConfigParser()
            parser.load_config("DefinitelY_not_existent")

    def test_load_config_removes_comments(self):
        expected = {'autostart': 'true', 'stderr_logfile': 'syslog'}
        loaded = self.execute_load_config("/env_files/test_comment.conf")

        self.assertDictEqual(expected, loaded)

    def test_load_config_can_load_simple_file(self):
        expected = {'autostart': 'true', 'autorestart': 'true', 'stderr_logfile': 'syslog'}
        loaded = self.execute_load_config("/env_files/simple_success.conf")

        self.assertDictEqual(expected, loaded)

    def test_invalid_option_raises_exception(self):
        with self.assertRaises(ParseError) as e:
            self.execute_load_config("/env_files/invalid_option.conf")

    def test_load_config_handles_multi_line_env(self):
        expected = {'autostart': 'true', 'autorestart': 'true', 'stderr_logfile': 'syslog',
                    'environment': 'TEST123="blabla",TEST456="987jep"'}
        loaded = self.execute_load_config("/env_files/env_variables.conf")

        self.assertDictEqual(expected, loaded)

    def test_load_config_handles_single_line_env(self):
        expected = {'autostart': 'true', 'autorestart': 'true', 'stderr_logfile': 'syslog',
                    'environment': 'TEST123="blabla",TEST456="987jep"'}
        loaded = self.execute_load_config("/env_files/single_line_env.conf")

        self.assertDictEqual(expected, loaded)

    def execute_load_config(self, file):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        parser = SupervisorConfigParser()
        return parser.parse_config(dir_path + file)


class TestCmdTwiddler(unittest.TestCase):
    @given(text())
    def test_twiddle_action_refuses_anything_but_add_or_remove(self, action):
        assume(action != "add")
        assume(action != "remove")
        with self.assertRaises(AttributeError):
            twiddle_command(action, "test_group", "test_program")


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
