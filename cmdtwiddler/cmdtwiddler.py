import os
import sys
import xmlrpclib
from pprint import pprint
from scriptine import run


def get_server_proxy():
    s = xmlrpclib.ServerProxy('http://localhost:9001', allow_none=True)

    return s


def handle_rpc_bad_name(fault):
    """
    Print nicely formatted RPC bad name fault. Include available supervisor groups and programs for easier debugging
    :param fault: xmlrpclib.Fault - Fault to display, must have faultCode 10
    """
    if not isinstance(fault, xmlrpclib.Fault) and fault.faultCode != 10:
        raise AttributeError("Only possible to handle rpc bad name faults")

    server = get_server_proxy()
    print_exception_context()

    print fault.faultString
    print "The following groups are registered"
    pprint(server.twiddler.getGroupNames())
    print ""
    print "The following programs are registered (with status)"
    programs = server.supervisor.getAllProcessInfo()
    for program in programs:
        print "{0} {1}".format(program['name'], program['statename'])

    sys.exit(1)


def print_exception_context():
    """
    Print File name and line number of raised exception.
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print (exc_type, fname, exc_tb.tb_lineno)

    print ""


def handle_rpc_fault(fault):
    """
    Print nice error message for relevant rpc faults. Re raise if unmanaged fault
    Also log all rpc errors to supervisor log
    :param fault: xmlrpclib.fault
    """
    if not isinstance(fault, xmlrpclib.Fault):
        raise AttributeError("Only possible to handle rpc faults")

    server = get_server_proxy()

    server.twiddler.log("Twiddler RPC fault ({0}): {1}".format(fault.faultCode, fault.faultString), "ERRO")

    if fault.faultCode == 10:
        handle_rpc_bad_name(fault)

    if fault.faultCode == 2:
        print_exception_context()
        print fault.faultString
        print "' \" : are forbidden characters. Alphanum , == and . are allowed"
        sys.exit(1)
    else:
        raise fault


def get_program_name(group_name, program_name):
    return group_name + ":" + program_name


def stop_program_when_running(group_name, program_name):
    """
    Stop a running supervisor program.
    :param group_name: str
    :param program_name: str
    :return: bool
    """
    server = get_server_proxy()

    try:
        info = server.supervisor.getProcessInfo(get_program_name(group_name, program_name))
        if info['statename'] == "RUNNING":  # no need to stop program
            result = server.supervisor.stopProcess(group_name + ":" + program_name)
        else:
            return True

    except xmlrpclib.Fault as e:
        raise handle_rpc_fault(e)

    return result


def remove(group_name, program_name):
    """
    Remove program from supervisor. Stop first if needed
    :param group_name:
    :param program_name:
    :return: bool
    """
    server = get_server_proxy()
    stop_program_when_running(group_name, program_name)
    try:
        result = server.twiddler.removeProcessFromGroup(group_name, program_name)
    except xmlrpclib.Fault as e:
        raise handle_rpc_fault(e)

    return result


def add(group_name, program_name, cmd):
    """
    Add program to supervisor group and try to start it. Deemed successful if program actually starts
    :param group_name: str - Group to which program should be attached
    :param program_name: str - Name of the program to register
    :param cmd: str - Actual command to execute
    :return: bool - True when succesfully added, false if not
    """
    server = get_server_proxy()

    try:
        server.twiddler.addProgramToGroup(group_name, program_name, {'command': cmd, 'autostart': "false"})
    except xmlrpclib.Fault as e:
        print "Unable to add program {0} to group {1}".format(program_name, group_name)
        raise handle_rpc_fault(e)

    try:
        result = server.supervisor.startProcess(group_name + ":" + program_name)
    except xmlrpclib.Fault as e:
        print "Unable to start program {0}".format(program_name)
        raise handle_rpc_fault(e)

    return result


def twiddle_command(action, group_name, program_name, cmd=None):
    """
    Add or remove a process to supervisor without restarting supervisor or any other processes
    :param action: Specify what action to execute, either "add" or "remove"
    :param group_name: Name of the group to which program should be added
    :param program_name: Name of the program being added
    :param cmd: Actual command that executes program (only when adding new program)
    """
    server = get_server_proxy()
    if action == 'add':
        result = add(group_name, program_name, cmd)
    elif action == "remove":
        result = remove(group_name, program_name)
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
