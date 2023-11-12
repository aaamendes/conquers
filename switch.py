import socket
# import time
# import random
import re
from pathlib import Path
from netmiko import ConnectHandler

class CsSwitchError(Exception):
    pass

# ConnectHandler Parameters
class ChParams:
    """
    Set `ConnectHandler <https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.ConnectHandler>`_ parameters

    Attributes:
        user (str): User name
        password (str): 
        host (str): The hostname to connect to (can be an IP address, too).
        device_type (str): e.g. "cisco_ios". 
            Check out netmiko's `documentation
            <https://ktbyers.github.io/netmiko/docs/netmiko/index.html>`_ for your device type.
            You can find, for example, the module ``netmiko.cisco`` under which the
            submodules represent the string that you need. So there is
            ``netmiko.cisco.cisco_ios`` and "cisco_ios" is, what you would use.
            
        conn_timeout (int): Connection timeout in seconds.
        read_timeout (float): Timeout for reading in seconds.
    """
    def __init__(self, **kwargs) -> None:
        self.user = ""
        self.password = ""
        self.host = ""
        self.device_type = ""
        self.conn_timeout = None
        self.read_timeout = None

        for k in kwargs:
            exec(f"self.{k} = kwargs[k]")

class CsSwitch:
    """
    Connects to a switch and sends the commands configured in the configuration
    file.

    Attributes:
        config (dict): pass

        params (:py:class:`~switch.ChParams`): 
            All the parameters needed for
            `netmiko <https://ktbyers.github.io/netmiko/docs/netmiko/>`_'s
            `ConnectHandler <https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.ConnectHandler>`_ 
            to connect to a switch.
            Populated with values from :py:class:`~switch.CsSwitch.config` for readabilty and it's easier to
            write the needed keys that way.
    """

    def __init__(self, config):
        self.config = config
        self.cmds = self.collect_commands()
        try:
            self.params = ChParams(
                user = self.config["credentials"]["user"],
                password = self.config["credentials"]["pass"],
                host = self.config["credentials"]["host"],
                device_type = self.config["settings"]["device_type"],
                conn_timeout = \
                    10 if "connection_timeout" not in self.config["settings"] \
                    else self.config["settings"]["connection_timeout"],
                read_timeout = \
                    10.0 if "read_timeout" not in self.config["settings"] \
                    else self.config["settings"]["read_timeout"]
            )
        except:
            raise CsSwitchError(
                "Credentials error. Probably no entry for host."
            )

        try:
            self.params.ip = socket.gethostbyname(self.params.host)
        except Exception as e:
            raise CsSwitchError(e) from e

        # Connect to switch
        try:
            self.device = ConnectHandler(
                device_type=self.params.device_type,
                ip=self.params.ip,
                username=self.params.user,
                password=self.params.password,
                conn_timeout=self.params.conn_timeout
            )
        except Exception as e:
            raise CsSwitchError(e) from e

    def send_cmds(self, cmd_set, type=None):
        """
        Sends commands distinguishing between configuration commands and show
        commands.
        This function is used by :py:class:`switch.CsSwitch.send_cmds_ba()` and
        :py:class:`switch.CsSwitch.send_conf_cmds()`.

        Args:
            cmd_set (list):
                List of dictionaries containing commands.
                Is built by :py:class:`switch.CsSwitch.split_into_sets()`.

                .. code-block:: python
                    :caption: Example for huawei changing the privilege level.

                    [
                        {
                            'special': {
                                'cmd': 'local-user admin privilege level 15'
                                'expect': [
                                    ('are your sure', 'Y')
                                ]
                            }
                        }
                    ]

            type (str):
                If ``type`` is ``None`` (default), configuration commands will be sent,
                show commands otherwise.
        """

        _output = ""

        for c in cmd_set:
            c_type = next(iter(c))

            if c_type == "set":
                try:
                    if type is None:
                        _output += self.device.send_config_set(
                            c[c_type],
                            read_timeout=self.params.read_timeout,
                            strip_prompt=True,
                            strip_command=True
                        ) + '\n'
                    else:
                        _output += self.device.send_multiline_timing(
                            c[c_type],
                            read_timeout=self.params.read_timeout,
                            strip_prompt=True,
                            strip_command=True
                        ) + '\n'
                except Exception as e:
                    raise CsSwitchError(e) from e
            elif c_type == "special":
                temp_out = self.device.send_command_timing(
                    (c[c_type]["cmd"]),
                    read_timeout=self.params.read_timeout
                )
                _output += temp_out

                for exp in c[c_type]["expect"]:
                    if exp[0] in temp_out:
                        temp_out = self.device.send_command_timing(
                            exp[1],
                            read_timeout=self.params.read_timeout,
                            strip_prompt=False,
                            strip_command=False
                        )
                        _output += temp_out

                _output += '\n'
            else:
                raise CsSwitchError("Command set not recognized.")

        return _output

    def send_cmds_ba(self, ba=None) -> str:
        """
        Send show commands.

        Args:
            ba (str): can be **after** or **before**
        """
        ba_allowed = [
            "before",
            "after"
        ]

        if ba not in ba_allowed:
            raise CsSwitchError('"before" or "after" must be passed')

        commands_set = self.split_into_sets(self.cmds[f"cmds_{ba}"])
        output = self.send_cmds(commands_set, "ba")

        return output

    def split_into_sets(self, cmds) -> list:
        """
        Commands that require interaction are treated specially.
        Here they are recognized by their syntax which is explained in the 
        `configuration <usage.html#configuration>`_.

        Regular commands are packed into lists which are sent altogether.
        Commands that require interaction are stuffed in between and executed
        differently making it possible to react to questions asked
        by the switch.
        """

        pattern = re.compile('#(.+?):(.+?);')
        commands_set = []
        temp_set = []

        for c in cmds:
            # matches is an array of tuples like
            # [('Are you sure?', 'yes'), ('Really?', 'yes'), ('Really really?', 'yes')]
            if matches := pattern.findall(c):
                if temp_set:
                    commands_set.append(
                        {
                            "set": temp_set
                        }
                    )

                    # reset temp_set for next temp_set
                    temp_set = []

                commands_set.append(
                    {
                        "special": {
                            "cmd": c.split("#")[0],
                            "expect": matches
                        }
                    }
                )
            else:
                temp_set.append(c)

        if temp_set:
            commands_set.append(
                {
                    "set": temp_set
                }
            )

        return commands_set

    def send_conf_cmds(self) -> str:
        """
        Send configuration commands.
        """

        if len(self.cmds["conf_cmds"]) == 0:
            return ""

        # Enter configuration mode.
        use_conf_cmd = "config_mode" in self.config["settings"]
        use_e_conf_cmd = "exit_config_mode" in self.config["settings"]

        try:
            if use_conf_cmd:
                self.device.config_mode(
                    config_command=self.config["settings"]["config_mode"]
                )
            else:
                self.device.config_mode()
        except Exception as e:
            raise CsSwitchError(
                "\nFailed to enter configuration mode.\n" +
                "Try setting config_mode in the configuration.\n"
            ) from e

        commands_set = self.split_into_sets(self.cmds["conf_cmds"])
        output = self.send_cmds(commands_set)

        # Exit configuration mode.
        try:
            if use_e_conf_cmd:
                self.device.exit_config_mode(
                    exit_config=self.config["settings"]["exit_config_mode"]
                )
            else:
                self.device.exit_config_mode()
        except Exception as e:
            raise CsSwitchError(
                "\nFailed to exit configuration mode.\n" +
                "Try setting exit_config_mode in the configuration.\n"
            ) from e

        return output

    def save_config(self) -> None:
        """
        Since netmiko's `save_config
        <https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.BaseConnection.save_config>`_ method is not implemented for
        the class `BaseConnection
        <https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.BaseConnection>`_,
        it is necessary to define `expect` and
        `answer` strings in `conquers.yaml` to identify the string to
        look for in the output and answer accordingly. This is possible with
        `netmiko`:

        .. code-block:: python
            :caption: Like so

            output = device.send_command_timing(c, read_timeout=READTIMEOUT)
            if "Are you sure" in output:
                output += device.send_command_timing(
                    "Y",
                    read_timeout=READTIMEOUT,
                    strip_prompt=False,
                    strip_command=False
                )

        Note:
            * not implemented
            * see :py:class:`switch.CsSwitch.split_into_sets()` for\
                    information on how it's possible to do it using a special\
                    syntax in the `configuration <usage.html#configuration>`_ file.
        """

    def collect_commands(self) -> dict:
        """
        Creates a dictionary like

        .. code-block:: python

            {
                "cmds_before": [],
                "cmds_after": [],
                "conf_cmds": []
            }

        from :py:class:`~switch.CsSwitch.config`.

        If available, add the commands from files defined in the configuration
        with something like this:

            * ``cmds_before_file: /path/to/file``
            * ``cmds_after_file: /path/to/file``
            * ``conf_cmds_file: /path/to/file``
        """

        create_cmd_arrays = [
            "cmds_before",
            "cmds_after",
            "conf_cmds"
        ]

        for arr in create_cmd_arrays:
            globals()[f"{arr}"] = []

            if arr in self.config["settings"]:
                for cmd in self.config["settings"][arr]:
                    eval(f"{arr}.append(cmd)")

            if f"{arr}_file" in self.config["settings"]:
                path = self.config["settings"][f"{arr}_file"].replace(
                    "~", str(Path.home())
                )
                file = None
                if Path(path).is_file():
                    try:
                        file = open(path, "r")
                    except Exception as e:
                        raise CsSwitchError(e) from e
                else:
                    raise CsSwitchError(f"File {path} does not exist.")

                lines = file.readlines()
                file.close()

                for l in lines:
                    l = l.rstrip()
                    # ignore comments
                    if l[:1] == "#":
                        continue

                    eval(f"{arr}.append(l)")

        return {
            "cmds_before": cmds_before,
            "cmds_after": cmds_after,
            "conf_cmds": conf_cmds
        }
