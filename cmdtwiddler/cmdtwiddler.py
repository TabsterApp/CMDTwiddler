#!/usr/bin/env python
import os
import sys
import xmlrpclib
from scriptine import run

from RPCHelper import RPCHelper
from supervisor_conf_file_parser import SupervisorConfigParser


class CMDTwiddler():
    def __init__(self):
        self.rpc_helper = RPCHelper()

    def get_program_name(self, group_name, program_name):
        return group_name + ":" + program_name

    def stop_program_when_running(self, group_name, program_name):
        """
        Stop a running supervisor program.
        :param group_name: str
        :param program_name: str
        :return: bool
        """
        server = self.rpc_helper.get_server_proxy()

        try:
            info = server.supervisor.getProcessInfo(self.get_program_name(group_name, program_name))
            if info['statename'] != "RUNNING":  # no need to stop program
                return True

            result = server.supervisor.stopProcess(group_name + ":" + program_name)

        except xmlrpclib.Fault as e:
            raise self.rpc_helper.handle_rpc_fault(e)
        except xmlrpclib.ProtocolError as e:
            print e.message
            print "Make sure /etc/cmdtwiddler/cmdtwiddler.ini exists, is readable and contains supervisor username and password"
            exit(1)

        return result

    def remove(self, group_name, program_name):
        """
        Remove program from supervisor. Stop first if needed
        :param group_name:
        :param program_name:
        :return: bool
        """
        server = self.rpc_helper.get_server_proxy()
        self.stop_program_when_running(group_name, program_name)
        try:
            result = server.twiddler.removeProcessFromGroup(group_name, program_name)
        except xmlrpclib.Fault as e:
            raise self.rpc_helper.handle_rpc_fault(e)

        return result

    def add(self, group_name, program_name, cmd, config_file=None):
        """
        Add program to supervisor group and try to start it. Deemed successful if program actually starts
        :param group_name: str - Group to which program should be attached
        :param program_name: str - Name of the program to register
        :param cmd: str - Actual command to execute
        :return: bool - True when succesfully added, false if not
        """
        server = self.rpc_helper.get_server_proxy()

        try:
            if config_file:
                parser = SupervisorConfigParser()
                config = parser.load_config(config_file)
                config['command'] = cmd
                server.twiddler.addProgramToGroup(group_name, program_name, config)
            else:
                server.twiddler.addProgramToGroup(group_name, program_name, {'command': cmd})

        except xmlrpclib.Fault as e:
            print "Unable to add program {0} to group {1}".format(program_name, group_name)
            raise self.rpc_helper.handle_rpc_fault(e)
        except xmlrpclib.ProtocolError as e:
            print e.message
            print "Make sure /etc/cmdtwiddler/cmdtwiddler.ini exists, is readable and contains supervisor username and password"
            exit(1)

        try:
            result = server.supervisor.startProcess(group_name + ":" + program_name)
        except xmlrpclib.Fault as e:
            print "Unable to start program {0}".format(program_name)
            raise self.rpc_helper.handle_rpc_fault(e)

        return result


def twiddle_command(action, group_name, program_name, cmd=None, config_file=None):
    """
    Add or remove a process to supervisor without restarting supervisor or any other processes
    :param action: Specify what action to execute, either "add" or "remove"
    :param group_name: Name of the group to which program should be added
    :param program_name: Name of the program being added
    :param cmd: Actual command that executes program (only when adding new program)
    :param config_file: File containing configuration for supervisor process - should be like normal supervisor config
    file without program definition
    """
    rpc_helper = RPCHelper()
    server = rpc_helper.get_server_proxy()

    cmd_twiddler = CMDTwiddler()
    if action == 'add':
        result = cmd_twiddler.add(group_name, program_name, cmd, config_file)
    elif action == "remove":
        result = cmd_twiddler.remove(group_name, program_name)
    else:
        raise AttributeError("It is only possible to add or remove a process to supervisor using cmdtwiddler")

    if result:
        print "Succesfully executed {0} {1}".format(action, program_name)
        server.twiddler.log("Succesfully executed {0} {1}".format(action, program_name))
        sys.exit(0)
    else:
        print "Unable to {0} {1}".format(action, program_name)
        server.twiddler.log("Unable to {0} {1}".format(action, program_name))
        sys.exit(1)


def main():
    run()
