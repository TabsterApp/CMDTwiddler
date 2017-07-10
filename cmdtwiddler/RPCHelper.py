import os, sys
import xmlrpclib
from ConfigParser import NoSectionError
from ConfigParser import SafeConfigParser, NoOptionError
from pprint import pprint


def print_exception_context():
    """
    Print File name and line number of raised exception.
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print (exc_type, fname, exc_tb.tb_lineno)

    print ""


class RPCHelper():
    def load_config(self):
        """
        Load user provided configuration
        :return: (str,str) Tuple of username and password
        """
        try:
            config = SafeConfigParser(os.environ)
            config.read('/etc/cmdtwiddler/cmdtwiddler.ini')

            user = config.get('supervisord', 'username')
            password = config.get('supervisord', 'password')
        except NoSectionError as e:
            # suppres error for now, username and password might not be required by supervisor
            user = ''
            password = ''
        except NoOptionError as e:
            print "Missing required config option"
            print e.message
            exit(1)

        return user, password

    def get_server_proxy(self):
        """
        Load xml rpc Server proxy. In case configuration is provided this is used (user/pass)
        :return: ServerProxy
        """
        user, password = self.load_config()

        try:
            if len(user) == 0 and len(password) == 0:
                s = xmlrpclib.ServerProxy('http://localhost:9001', allow_none=True)
            else:
                s = xmlrpclib.ServerProxy('http://' + user + ':' + password + '@localhost:9001', allow_none=True)
        except xmlrpclib.ProtocolError as e:
            print e.message
            print "Make sure /etc/cmdtwiddler/cmdtwiddler.ini exists, is readable and contains supervisor username and password"
            exit(1)

        return s

    def handle_rpc_bad_name(self, fault):
        """
        Print nicely formatted RPC bad name fault. Include available supervisor groups and programs for easier debugging
        :param fault: xmlrpclib.Fault - Fault to display, must have faultCode 10
        """
        if not isinstance(fault, xmlrpclib.Fault) and fault.faultCode != 10:
            raise AttributeError("Only possible to handle rpc bad name faults")

        server = self.get_server_proxy()
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

    def handle_rpc_fault(self, fault):
        """
        Print nice error message for relevant rpc faults. Re raise if unmanaged fault
        Also log all rpc errors to supervisor log
        :param fault: xmlrpclib.fault
        """
        if not isinstance(fault, xmlrpclib.Fault):
            raise AttributeError("Only possible to handle rpc faults")

        server = self.get_server_proxy()

        server.twiddler.log("Twiddler RPC fault ({0}): {1}".format(fault.faultCode, fault.faultString), "ERRO")

        if fault.faultCode == 10:
            self.handle_rpc_bad_name(fault)

        if fault.faultCode == 2:
            print_exception_context()
            print fault.faultString
            print "' \" : are forbidden characters. Alphanum , == and . are allowed"
            sys.exit(1)
        else:
            raise fault
