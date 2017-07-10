# CMDTwiddler
Small wrapper for twiddler to add and remove supervisor processes on the fly from the command line

Installation
-------------
After installing the package, add these lines to your supervisord.conf file to register the twiddler interface:

[rpcinterface:twiddler]
After installing the package, add these lines to your ``supervisord.conf`` file
to register the twiddler interface:

.. code-block:: ini

    [rpcinterface:twiddler]
    supervisor.rpcinterface_factory = supervisor_twiddler.rpcinterface:make_twiddler_rpcinterface

You must restart Supervisor for the twiddler interface to be loaded.

Running
--------
Usage: ```cmdtwiddler twiddle [options] action group_name program_name```

 Add or remove a process to supervisor without restarting
supervisor or any other processes :param action: Specify
what action to execute, either "add" or "remove" :param
group_name: Name of the group to which program should be
added :param program_name: Name of the program being added
:param cmd: Actual command that executes program (only when
adding new program)

Required arguments:
- action: Specify what action to execute, either "add" or "remove"
- group_name: Name of the group to which program should be added
- program_name: Name of the program being added