from pathlib import Path
import json
import yaml
from colorama import init, Fore, Style
from constants import Constants as Const

init(autoreset=True)            # Reset color.

class CollectorError(Exception):
    pass

class Collector:
    """
    A class to collect, format and print information gathered from hosts.

    Attributes:
        json_indentation (int):
            The default is ``4``. It can be changed in the configuration.

            .. code-block:: yaml
                :caption: Configure json indentation

                ---
                defaults:
                  report_types:
                    - html
                    - json:2

        htmltop (str): 
            html snippet for html report.
            See :py:class:`constants.Constants.HTML_TOP`.

        htmlbottom (str): 
            html snippet for html report.
            See :py:class:`constants.Constants.HTML_BOTTOM`.

        collected_objects (list): 
            .. code-block:: python
                :caption: Something like this depending on the configuration

                [
                	{
                		"group": "awesomegroup",
                		"host": "some-switch",
                		"errors": [],
                		"rc": 0,
                		"output": {
                			"cmds_before": [
                				"ip name-server 8.8.8.8"
                			],
                			"cmds_after": [
                				"ip name-server 9.9.9.9"
                			]
                		},
                		"message": "ok",
                		"config": {
                			"settings": {
                				"device_type": "cisco_ios",
                				"connection_timeout": 10,
                				"read_timeout": 10,
                				"silent": True,
                				"conf_cmds": [
                					"no ip name-server 8.8.8.8",
                					"ip name-server 9.9.9.9"
                				],
                				"cmds_before": [
                					"show run | include name-server"
                				],
                				"cmds_after": [
                					"show run | include name-server"
                				],
                				"log_file": "~/.conquers/some-switch.log"
                			},
                			"credentials": {
                				"user": "admin",
                				"host": "some-switch",
                				"encrypted_pass": "********",
                				"pass": "********"
                			}
                		}
                	},
                ]

        hosts_by_group (dict):
            .. code-block:: python
                :caption: Something like this depending on the configuration

                {
                    "awesomegroup": [
                        {
                            "another-switch": {
                                "errors": [],
                                "rc": null,
                                "message": "skipped",
                                "config": {
                                    "host": "another-switch",
                                    "settings": {
                                        "device_type": "cisco_ios",
                                        "connection_timeout": 10,
                                        "read_timeout": 10,
                                        "silent": true
                                    },
                                    "credentials": false
                                }
                            }
                        },
                        {
                            "some-switch": {
                                "errors": [],
                                "rc": 0,
                                "output": {
                                    "cmds_before": [
                                        "ip name-server 8.8.8.8"
                                    ],
                                    "cmds_after": [
                                        "ip name-server 9.9.9.9"
                                    ]
                                },
                                "message": "ok",
                                "config": {
                                    "settings": {
                                        "device_type": "cisco_ios",
                                        "connection_timeout": 10,
                                        "read_timeout": 10,
                                        "silent": true,
                                        "conf_cmds": [
                                            "no ip name-server 8.8.8.8",
                                            "ip name-server 9.9.9.9"
                                        ],
                                        "cmds_before": [
                                            "show run | include name-server"
                                        ],
                                        "cmds_after": [
                                            "show run | include name-server"
                                        ],
                                        "log_file": "~/.conquers/some-switch.log"
                                    },
                                    "credentials": {
                                        "user": "admin",
                                        "host": "some-switch",
                                        "encrypted_pass": "********",
                                        "pass": "********"
                                    }
                                }
                            }
                        }
                    ],
                    "anothergroup": [
                        "..."
                    ],
                }

    """

    def __init__(self):
        self.collected_objects = []
        self.hosts_by_group = {}
        self.json_indentation = 4
        self.htmltop = Const.HTML_TOP
        self.htmlbottom = Const.HTML_BOTTOM

    def add_to_collection(self, item) -> None:
        """
        Adds **item** to **collected_objects**

        Parameters
        ----------
        item : dict
            Object to add
        """
        self.collected_objects.append(item)

    def __build_complete_summary(self) -> None:
        for host_item in self.collected_objects:
            # Create group if it doesn't exist.
            if host_item["group"] not in self.hosts_by_group:
                self.hosts_by_group[host_item["group"]] = []

            # Create host object with keys and values.
            host = {}
            for key in host_item:
                if key == "group" or key == "host":
                    continue

                host[key] = host_item[key]

            # Add host to group
            self.hosts_by_group[host_item["group"]].append(
                {
                    host_item["host"]: host
                }
            )

    def log_to_report(self) -> None:
        """
        Logs a full report if configured in the configuration file.
        Three output format are possible:
            * html (fancy, recommended for humans)
            * yaml
            * json or json:<indentation>
        """

        try:
            report_types = self.collected_objects[0]["config"]["settings"]["report_types"]
        # report_types is not defined in the configuration -> do nothing.
        except Exception as e:
            report_types = ""

        if "yaml" in report_types:
            with open(f"{Const.CHOME_ABS_PATH}/report.yaml", "w", encoding="utf-8") as fh:
                fh.write(yaml.dump(self.hosts_by_group))

        for rep_t in report_types:
            if "json" in rep_t:
                try:
                    indentation = rep_t.split(":")[1]

                    if indentation.isdigit():
                        self.json_indentation = int(indentation)
                except IndexError as e:
                    pass

                with open(f"{Const.CHOME_ABS_PATH}/report.json", "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(self.hosts_by_group,
                                        indent=self.json_indentation))

                break

        if "html" in report_types:
            with open(f"{Const.CHOME_ABS_PATH}/report.html", "w", encoding="utf-8") as fh:
                fh.write(self.htmltop)

                for group in self.hosts_by_group:
                    # fh.write('<li class="group-entry">' + group + 
                    #     '</li><li class="sub-li"><ul class="hosts-nav-sub">')
                    fh.write('\t\t\t\t\t\t\t<li class="group-entry">\n')
                    fh.write('\t\t\t\t\t\t\t\t' + group + '\n')
                    fh.write('\t\t\t\t\t\t\t</li>\n')
                    fh.write('\t\t\t\t\t\t\t<li class="sub-li">\n')
                    fh.write('\t\t\t\t\t\t\t\t<ul class="hosts-nav-sub">\n')

                    for h in self.hosts_by_group[group]:
                        temp_group = {
                            group: []
                        }
                        temp_group[group].append(h)
                        # fh.write('<li class="sub-li-item" data-json=\'' +
                        # json.dumps(temp_group).replace("'", "\'") + 
                        # '\'>' + next(iter(h)) + '</li>')
                        fh.write('\t\t\t\t\t\t\t\t\t')
                        fh.write('<li class="sub-li-item" ')
                        fh.write('data-json=\'' +
                            json.dumps(temp_group).replace("'", "\'") + 
                            '\'>' + next(iter(h)) + '</li>\n')

                    fh.write('\t\t\t\t\t\t\t\t</ul>\n')
                    fh.write('\t\t\t\t\t\t\t</li>')

                fh.write(self.htmlbottom)

    def log_to_file(self, data) -> None:
        """
        If **log_file** is specified in the configuration, the output 
        of commands sent to a swtich and information about the host
        are logged to this file.
        """

        if "log_file" not in data["config"]["settings"]:
            return

        log_file = data["config"]["settings"]["log_file"].replace(
            "~", str(Path.home())
        )

        try:
            fh = open(log_file, "w")
        except OSError as e:
            raise CollectorError(e) from e

        for cmdout in data["output"]:
            for line in data["output"][cmdout]:
                fh.write(f"{line}\n")

        fh.close()

    def hide_passwords(self, data) -> None:
        """
        Overrides password strings with * for console output.

        Parameters
        ----------
            data : dict
        """

        if "credentials" in data["config"]:
            if "pass" in data["config"]["credentials"]:
                data["config"].pop("host", None)
                data["config"]["credentials"]["encrypted_pass"] = "********"
                data["config"]["credentials"]["pass"] = "********"

    def print_single_summary(self, data) -> None:
        """
        Print collected info in yaml format to the console. 
        This can be silenced by setting **silent** to **true** in the
        configuration.
        """

        # Do not print if silent.
        if "silent" in data["config"]["settings"]:
            if data["config"]["settings"]["silent"]:
                return

        yaml_data = yaml.dump(data)

        for line in yaml_data.splitlines():
            Collector.print_extra_info(f"    {line}")

    def __format_line_summary(self, group, host, *strings) -> str:
        g_max_len = 18
        max_len = 13
        result = ""

        if len(group) >= g_max_len:
            group = "{}...".format(group[:g_max_len])

        if len(host) >= g_max_len:
            host = "{}...".format(host[:g_max_len])

        result += "{:<21}".format(group)
        result += "{:<21}".format(host)

        for v in strings:
            if len(v) >= max_len:
                v = "{}...".format(v[:max_len])

            result += "{:<15}".format(v)

        return result

    def print_complete_summary(self) -> None:
        """
        Print brief information about completed hosts in a table.
        """

        self.__build_complete_summary()
        print("\n\n")
        Collector.print_info(
            self.__format_line_summary(
                "Group", "Host", "Device", "Msg", "Err", "Log"
            )
        )
        for i in range(0,90):
            Collector.print_info("-", end="")
        print("")

        for g in self.hosts_by_group:
            for h in self.hosts_by_group[g]:
                switch = next(iter(h))
                errors = len(h[switch]["errors"])
                message = h[switch]["message"]
                device = h[switch]["config"]["settings"]["device_type"]
                if "log_file" in h[switch]["config"]["settings"]:
                    log = "yes"
                else:
                    log = "no"

                if errors > 0:
                    errors = str(errors)
                    Collector.print_error(
                        self.__format_line_summary(
                            g, switch, device, message, errors, log
                        )
                    )
                elif message == "skipped":
                    errors = str(errors)
                    Collector.print_warning(
                        self.__format_line_summary(
                            g, switch, device, message, errors, log
                        )
                    )
                else:
                    errors = str(errors)
                    Collector.print_mild_info(
                        self.__format_line_summary(
                            g, switch, device, message, errors, log
                        )
                    )

    @staticmethod
    def print_info(string, **kwargs) -> None:
        """
        Print to console in bright green.
        """

        print(f"{Style.BRIGHT}{Fore.GREEN}{string}", **kwargs)

    @staticmethod
    def print_mild_info(string, **kwargs) -> None:
        """
        Print to console in normal green.
        """

        print(f"{Style.NORMAL}{Fore.GREEN}{string}", **kwargs)

    @staticmethod
    def print_error(string, **kwargs) -> None:
        """
        Print error to console in red.
        """

        print(f"{Style.NORMAL}{Fore.RED}{string}", **kwargs)

    @staticmethod
    def print_warning(string, **kwargs) -> None:
        """
        Print a warning to console in purple.
        """

        print(f"{Style.NORMAL}{Fore.MAGENTA}{string}", **kwargs)

    @staticmethod
    def print_extra_info(string, **kwargs) -> None:
        """
        Prints additional information in grey.
        """

        print(f"{Style.NORMAL}{Fore.LIGHTBLACK_EX}{string}", **kwargs)
