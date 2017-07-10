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