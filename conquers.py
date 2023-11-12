#!/usr/bin/env python3

import sys
import os
import math
import argparse
import socket
import json
from copy import deepcopy
from inspect import currentframe, getframeinfo
from pathlib import Path
import signal
import psutil
# conquers libraries
import utilities as util
from credentials import\
        Credentials,\
        MasterkeyError,\
        CredentialsError
from configuration import Config
from switch import\
        CsSwitch,\
        CsSwitchError
from constants import Constants
from collector import\
        Collector,\
        CollectorError

# Set CHOME_ABS_PATH
Constants.set_abs_path()
# Create conquers home if it doesn't exist.
if not os.path.exists(Constants.CHOME_ABS_PATH):
    os.makedirs(Constants.CHOME_ABS_PATH)

# Create empty credentials file, if it doesn't exist.
if not Path(f"{Constants.CHOME_ABS_PATH}/credentials").is_file():
    Path(f"{Constants.CHOME_ABS_PATH}/credentials").touch()

# Remove socket file if it still exists.
if os.path.exists(Constants.SOCKET_FILE):
    os.remove(Constants.SOCKET_FILE)

def main():
    """
    Todo:
        * description
    """

    # Catch ctrl-c and clean up
    signal.signal(signal.SIGINT, catch_and_cleanup)

    # Parse arguments.
    parser = argparse.ArgumentParser(description=f"{Constants.VERSION}")
    args = parse_options(parser)

    ####################################################### 
    # Use utilities?                                      #
    ####################################################### 
    # Convert public key
    if args.public_key is not None:
        if args.device_type is None:
            Collector.print_warning("Please specify device type with -d.")
            Collector.print_warning("Currently known formats are cisco_ios and " + 
                                    "huawei.")
            sys.exit(1)

        util.decide_pub_key_method(args.public_key, args.device_type)

    ####################################################### 

    # Add entry to credentials file.
    if args.add_credentials is not None:
        add_cred = Credentials(args.credentials, args.masterkey)
        add_cred.checks_add_entry()
        sys.exit(0)
    # Parse configuration from file.
    config = get_configuration(args)

    if config is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Get Masterkey if not privided.
    if args.masterkey is None:
        try:
            args.masterkey = Credentials(args.credentials, None).master_key.decode()
        except MasterkeyError as e:
            print(e)
            sys.exit(1)

    # Create config objects for every switch.
    cs_config_objs = gen_switch_config_objects(config)

    for group in cs_config_objs:
        for h in group["hosts"]:
            try:
                h['credentials'] = Credentials(
                    args.credentials,
                    args.masterkey
                ).return_credentials(h['host'])
            except CredentialsError as e:
                print(e)
                sys.exit(1)

    # UNIX SOCKET listen.
    s_listen = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s_listen.bind(Constants.SOCKET_FILE)
    s_listen.listen(0)

    coll = Collector()

    #########################################################
    # Let's start forking.                                  #
    #########################################################
    for obj in cs_config_objs:
        Collector.print_info(
            f'[GROUP] {obj["group"]}, forks: {obj["forks"]}'
        )

        # Determine fork_rounds.
        fork_rounds = math.ceil(len(obj["hosts"]) / obj["forks"])
        forks = obj["forks"]

        for i in range(0, fork_rounds):
            pids = []
            for host in obj["hosts"][(i*forks):(i*forks)+forks]:
                Collector.print_mild_info(f'   *    {host["host"]}')

                if host["credentials"] is False:
                    Collector.print_warning(
                        f'   ✝    {host["host"]} No credentials found, skipping ...'
                    )

                    coll.add_to_collection({
                        "group": obj["group"],
                        "host": host["host"],
                        "errors": [],
                        "rc": None,
                        "message": "skipped",
                        "config": host
                    })

                    continue

                pid = os.fork()

                if pid == 0:
                    # Define output structure per forked host.
                    output_object = {
                        "group": obj["group"],
                        "host": host["host"],
                        "errors": [],
                        "rc": 0,
                        "output": {
                            "cmds_before": [],
                            "cmds_after": [],
                            "conf_cmds": []
                        },
                        "message": "",
                        # Add config for host.
                        "config": host
                    }
                    # UNIX SOCKET
                    s_conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                    try:
                        csswitch = CsSwitch(host)
                    except CsSwitchError as e:
                        frameinfo = getframeinfo(currentframe())
                        socket_send_info(s_conn, output_object, frameinfo, e)
                        sys.exit(1)

                    # Send BEFORE commands.
                    try:
                        output = csswitch.send_cmds_ba("before")
                        for line in output.splitlines():
                            output_object["output"]["cmds_before"].append(line)
                    except CsSwitchError as e:
                        frameinfo = getframeinfo(currentframe())
                        socket_send_info(s_conn, output_object, frameinfo, e)
                        sys.exit(1)

                    # Send CONFIG commands.
                    try:
                        output = csswitch.send_conf_cmds()
                        for line in output.splitlines():
                            output_object["output"]["conf_cmds"].append(line)
                    except CsSwitchError as e:
                        frameinfo = getframeinfo(currentframe())
                        socket_send_info(s_conn, output_object, frameinfo, e)
                        sys.exit(1)

                    # Send AFTER commands.
                    try:
                        output = csswitch.send_cmds_ba("after")
                        for line in output.splitlines():
                            output_object["output"]["cmds_after"].append(line)
                    except CsSwitchError as e:
                        frameinfo = getframeinfo(currentframe())
                        socket_send_info(s_conn, output_object, frameinfo, e)
                        sys.exit(1)

                    output_object["message"] = "ok"
                    socket_send_info(s_conn, output_object)
                    sys.exit(0)             # exit forked process
                else:
                    pids.append(pid)
                    os.waitpid(pid, 1)

            #######################################################
            # Wait for pids.                                      #
            #######################################################
            for pid in pids:
                conn, addr = s_listen.accept()
                data = ""
                data_json = {}

                while True:
                    data_bin = conn.recv(Constants.BUFF_SIZE)
                    if data_bin == b"":
                        break
                    data += data_bin.decode()

                try:
                    data_json = json.loads(data)
                except json.decoder.JSONDecodeError as e:
                    Collector.print_error(f'   ⨯    {data_json["host"]}')
                    Collector.print_error(f"         {e}")
                    sys.exit(1)

                if data_json["errors"]:
                    Collector.print_error(f'   ⨯    {data_json["host"]}')
                    Collector.print_error(f'        {data_json["errors"][0]}')
                else:
                    Collector.print_info(f'   ✓    {data_json["host"]}')

                # If log_file is defined, log output.
                try:
                    coll.log_to_file(data_json)
                except CollectorError as e:
                    coll.print_warning(f'   !    {e}')
                # Hide passwords in console output.
                coll.hide_passwords(data_json)
                # The single summary can be silenced in the configuration with
                # silent: true
                coll.print_single_summary(data_json)
                # -------------------------------------------------------
                coll.add_to_collection(data_json)
                # -------------------------------------------------------
                os.waitpid(pid, 0)
            # ---- for pid in pids END ------------------------------
    # ---- for obj in cs_config_objs END --------------------

    s_listen.close()
    # Clean up remote socket file.
    if os.path.exists(Constants.SOCKET_FILE):
        os.remove(Constants.SOCKET_FILE)
    ########################################################
    # print collected data from UNIX SOCKET nicely         #
    # and in color :)                                      #
    ########################################################
    coll.print_complete_summary()
    coll.log_to_report()
# ---- main() END --------------------------------------------------------------

def catch_and_cleanup(signum, frame):
    """
    Kill all forked processes and exit.
    """

    parent = psutil.Process()
    children = parent.children(recursive=True)

    for child in children:
        killed = True
        Collector.print_warning(f"Child pid {child.pid} ", end="")
        c = psutil.Process(child.pid)

        try:
            c.terminate()
        except Exception as e:
            Collector.print_error(f"! Cannot kill {child.pid}.")
            killed = False

        if killed:
            Collector.print_info("[KILLED]")

    sys.exit(0)

def socket_send_info(sock, output_object, frameinfo=None, exception=None):
    """
    Todo:
        * description
    """

    if exception is not None:
        output_object["errors"].append(
            # f"Exception: {exception} ({__file__}:{frameinfo.lineno})"
            f"Exception: {exception}"
        )
        output_object["message"] = "failed"
        output_object["rc"] = 1

    output_object = json.dumps(output_object)

    sock.connect(Constants.SOCKET_FILE)
    sock.sendall(output_object.encode())
    sock.close()
# ---- socket_send_info() END --------------------------------------------------

def parse_options(parser):
    """
    Todo:
        * description
    """
    parser.add_argument("--add-credentials", required=False,
                        default=None,
                        action="store_true",
                        help=f"""Add entry to credentials.
                        Specify credentials file with --credentials,
                        the default is {Constants.CHOME}credentials""")
    parser.add_argument("--credentials", default=f"{Constants.CHOME}credentials",
                        help=f"""Path to credentials file.
                        Default is {Constants.CHOME}credentials""")
    parser.add_argument("--config",
                        default=f"{Constants.CHOME}{Constants.DEFAULT_CONFIG}",
                        help=f"""Path to configuration file. Default is
                        {Constants.CHOME}{Constants.DEFAULT_CONFIG}""",
                        required=False)
    parser.add_argument("-m",
                        "--masterkey",help="""Path to file containing the
                        master key""".replace("\n", " "), required=False)
    parser.add_argument("-d", "--device-type",
                        help="Like cisco_ios or huawei.",
                        default=None,
                        required=False
                       )
    parser.add_argument("-p", "--public-key",
                        help="Converts public key to format specified with -d.",
                        default=None,
                        required=False
                       )

    return parser.parse_args()
# ---- parse_options() END ---------------------------------------------------

def get_configuration(args):
    """
    Todo:
        * description
    """
    chkconfig = Config(args.config)
    chkconfig.check()
    chkconfig.parse()

    if not chkconfig.errors:
        return chkconfig.return_config()

    for e in chkconfig.errors:
        print(e)
    return None
# ---- get_configuration() END -------------------------------------------------

def gen_switch_config_objects(config):
    """
    Todo:
        * description
    """

    objects = []
    groups = []
    exclude = ['forks']

    for group in config:
        # set top defaults
        defaults_top = deepcopy(config['defaults'])
        # skip defaults, it's not a group
        if group == "defaults":
            continue

        group_defaults = deepcopy(defaults_top)

        for default_val in config[group]:
            # skip hosts
            if default_val == "hosts":
                continue

            # set setting or override defaults
            group_defaults[default_val] = deepcopy(config[group][default_val])

        for key in config[group]:
            if key != "hosts":
                continue

            settings = {}
            for obj in config[group][key]:
                switch = next(iter(obj))
                settings[switch] = deepcopy(group_defaults)

                # remove excludes
                for e in exclude:
                    settings[switch].pop(e, None)

                if obj[switch] is None:
                    # add object
                    objects.append(
                        {
                            "host": switch,
                            "settings": settings[switch]
                        }
                    )
                    # has no keys -> continue
                    continue

                # set or override defaults
                for attrib_key, attrib_val in obj[switch].items():
                    # skip excludes
                    if attrib_key in exclude:
                        continue

                    settings[switch][attrib_key] = attrib_val

                    # remove excludes
                    for e in exclude:
                        settings[switch].pop(e, None)

                # add object
                objects.append(
                    {
                        "host": switch,
                        "settings": settings[switch]
                    }
                )
                # ---- for attrib_key END ----------
            # ---- for ob in config END---------
        # ---- for key in config[group] END

        groups.append(
            {
                "group": group,
                "forks": group_defaults["forks"] if \
                    group_defaults["forks"] is not None else defaults_top["forks"],
                "hosts": objects
            }
        )
        objects = []

    # ---- for group in config END -----

    return groups
# ---- gen_switch_config_objects() END -----------------------------------------

if __name__ == "__main__":
    main()
