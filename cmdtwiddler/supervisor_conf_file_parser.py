import codecs
import os

__escape_decoder = codecs.getdecoder('unicode_escape')


def decode_escaped(escaped):
    return __escape_decoder(escaped)[0]


class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class SupervisorConfigParser():
    allowed_keys = {"numprocs", "numprocs_start", "priority", "autostart", "startsecs", "startretries", "autorestart",
                    "exitcodes", "stopsignal", "stopwaitsecs", "stopasgroup", "killasgroup", "user", "redirect_stderr",
                    "stdout_logfile", "stdout_logfile_backups", "stdout_capture_maxbytes", "stdout_events_enabled",
                    "stderr_logfile", "stderr_logfile_maxbytes", "stderr_logfile_backups", "stderr_capture_maxbytes",
                    "stderr_events_enabled", "environment", "directory", "umask", "serverurl"}

    def load_config(self, config_file):
        """
        Check if config file exists, and parse if so
        :param config_file:
        :return: dict
        """
        if not os.path.isfile(config_file):
            raise AttributeError("Unable to load environment file")

        return self.parse_config(config_file)

    def parse_config(self, config_file):
        """
        Parse supervisor config file to dictionary that can used by cmdtwiddler
        :param config_file: string
        :return: dict
        """
        with open(config_file) as f:
            parsed = {}
            parsing_env = False
            env = ""
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue

                k, v = line.split('=', 1)
                k, v = k.strip(), v.strip()

                if k == "environment":
                    parsing_env = True
                    env = v  # deal with single-line env
                elif parsing_env == True and k in self.allowed_keys:
                    parsing_env = False  # Finished parsing env

                if k not in self.allowed_keys:
                    if parsing_env == False:  # Invalid option
                        raise ParseError("Invalid option {0} in config file".format(k))
                    else:  # Deal with multi-line env
                        env += line
                else:
                    parsed[k] = v

            if len(env) > 0:
                parsed['environment'] = env

            return parsed
