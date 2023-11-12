conquers
=========

**conquers** (CONfigure and QUERy network Switches) is a python 
program to do what its name implies.

It makes use of the python `netmiko <https://github.com/ktbyers/netmiko>`_
library to do its work.

Usage
=====

Installation
------------

Clone the repository like so:

.. code-block:: console

    $ git clone https://github.com/medecaj/conquers

To use *conquers*, first install its requirements using pip:

.. code-block:: console

    $ cd conquers
    $ python3 -m pip install -r requirements.txt


Options
-------

.. code-block:: console

		$ ./conquers.py --help
		usage: conquers.py [-h] [--add-credentials] [--credentials CREDENTIALS] [--config CONFIG] [-m MASTERKEY] [-d DEVICE_TYPE] [-p PUBLIC_KEY]
		
		conquers v0.1
		
		options:
		  -h, --help            show this help message and exit
		  --add-credentials     Add entry to credentials. Specify credentials file with --credentials, the default is ~/.conquers/credentials
		  --credentials CREDENTIALS
		                        Path to credentials file. Default is ~/.conquers/credentials
		  --config CONFIG       Path to configuration file. Default is ~/.conquers/config.yaml
		  -m MASTERKEY, --masterkey MASTERKEY
		                        Path to file containing the master key
		  -d DEVICE_TYPE, --device-type DEVICE_TYPE
		                        Like cisco_ios or huawei.
		  -p PUBLIC_KEY, --public-key PUBLIC_KEY
		                        Converts public key to format specified with -d.


Configuration
-------------

*conquers* uses a configuration file to make use of its features. It must be in
``.yaml`` format. Here is ``config.yaml.example`` from the
`repository <https://github.com/medecaj/conquers/>`_:

.. code-block:: yaml


        ---
        # vim: se ft=yaml:
        # filename: config.yaml.example
        ################################################################################
        ###########    COMMANDS    #####################################################
        ################################################################################
        # There are three types of commands:
        #     - commands before configuration (cmds_before -> list)
        #     - configuration commands (conf_cmds -> list)
        #     - commands after configuration (cmds_after -> list)
        #
        # cmds_before and cmds_after are usually show commands.
        # One exception would be a command to make the configuration persistent like
        #     - write memory
        # Commands like that belong in cmds_after at the end.
        #
        # All configuration commands belong in **conf_cmds** and do not work in the
        # other sections.
        #
        # For large command sets you can specify a path to a file containing
        # commands, one per line:
        #     - cmds_before_file -> string
        #     - conf_cmds_file -> string
        #     - cmds_after_file -> string
        #
        # Find some EXAMPLES below.
        #
        # IMPORTANT:
        # ----------
        # Commands from e.g. cmds_before and cmds_after will be
        # combined where commands cmds_before_file will be added after cmds_before.
        #
        # EXPECTS:
        # --------
        # With a special syntax you can react to interactions.
        #
        # The string after # is a string that you expect to be contained in the
        # question. The string after the colon will be sent as an answer.
        # Multiple expects are possible, each one is terminated with a semicolon.
        # Example:
        # cmds_after:
        #   - "copy scp://server.com//var/www/file.bin flash:#username:yes;#filename:yes;"
        
        ################################################################################
        #############    DEFAULTS    ###################################################
        ################################################################################
        defaults:                                     # Is not a group name
          # Forks per group
          forks: 5
          device_type: "huawei"
          connection_timeout: 5                       # Default is 10
          read_timeout: 5                             # Default is 10
          # List of report types. CAN ONLY BE SET HERE.
          report_types:
          # Possible types are json, yaml and html
          # and can only be set in defaults.
          # report.<type> will be created in ~/.conquers.
            - html                                    # (fancy, recommended for humans)
            - yaml
            # For type json you can specify the indentation with
            #     :<number> (default:4)
            - json:2
          # If set to false, a yaml report is shown in the console per host.
          # EXCEPTIONS AND ERRORS ARE ALWAYS SHOWN IN THE CONSOLE.
          silent: false
        
        ################################################################################
        #############    GROUPS    #####################################################
        ################################################################################
        # ----------- EXAMPLE GROUP cisco ----------------------------------------------
        # Demostrates overriding settings and the defining of hosts.
        cisco:                                        # Group name
          silent: true                                # Overrides default
          device_type: "cisco_ios"                    # Overrides default
          forks: 10                                   # Overrides default
          #   config_mode 
          # and 
          #   exit_config_mode
          # are optional and not needed for device_type "cisco_ios" and are shown here
          # merely for demonstration.
          # Sould you encounter problems with configuration commands where it's not
          # possible to enter the configuration mode, try these settings with the
          # corresponding commands for your device to enter and exit configuration mode.
          config_mode: "conf t"                       # Enter conf (cisco_ios)
          exit_config_mode: "end"                     # Exit conf mode (cisco_ios)
          cmds_after:
            - "show run | include username"
          ###########    HOSTS    ######################################################
          hosts:
            - cs-access1:
                silent: false                         # Overrides group setting
            - cs-access2:                             # A colon is mandatory after host
        
        # ----------- EXAMPLE GROUP firmware_upgrade -----------------------------------
        # Example for a group where the hosts get a new firmware.
        # Demonstrates special syntax for interactions.
        firmware_upgrade:                             # Group name
          device_type: "cisco_ios"
          silent: true
          cmds_after:
            # The string after # is what you expect, the string after the colon will
            # be sent as an answer. A semicolon terminates the expression, multiple
            # expects are possible.
            - "copy scp://someserver.com//var/www/some.file flash:#username:yes;#filename:yes;"
          hosts:
            - cisco-core-1:
            - cisco-core-2:
              # different file only for cisco-core-2
              cmds_after:                             # Overrides group setting
                - "copy scp://diff.com//var/www/diff.file flash:#username:yes;#filename:yes;"
            - cisco-core-3:
            - cisco-core-4:
        
        # ----------- EXAMPLE GROUP logging --------------------------------------------
        # In this example, the complete configuration will be logged to
        # the specified log file.
        # With **log_file** the OUTPUT of every command will be logged.
        logging:
          device_type: "cisco_ios"
          silent: true
          cmds_before:
            - "show run"
          hosts:
            - cisco-core-1:
                log_file: "~/path/file.log"
            - cisco-core-2:
                log_file: "/path/to/file.log"

conquers in action
-------------------

.. raw:: html

    <video controls style="max-width:987px" poster="https://cdn.amendes.me/conquers/poster.svg">
        <source src="https://cdn.amendes.me/conquers/example.mp4"
        type="video/mp4" />
    </video>


Examples
--------
