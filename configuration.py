import os
import tomllib
from pathlib import Path
import yaml

class Config:
    """
    This class parses **conquers**'s configuration file, checks for errors and
    returns an object containing the configuration.

    The path to a yaml configuration file must be passed to the constructor.

    Attributes:
        config_file (str): A relative or absolute path to the yaml configuration file.
        config_object (dict): The configuration as a python dicationary.
        file_handle (file): The file handle used for the configuration file.
        file_extension (str): The file exentsion used for \
                the configuration file.
        valid_file_extensions (list): File extensions allowed to use.
        errors (list): Errors are collected here.
        required_keys (list): A list of keys that must be present \
                in the configuration per group or host.

    """

    def __init__(self, config_file) -> None:
        self.file_handle = None
        self.file_extension = None
        self.config_file = config_file
        self.config_object = None
        self.valid_file_extensions = [".yaml", ".yml"]
        self.errors = []
        self.required_keys = [
            "device_type",
        ]

    def check(self) -> bool:
        """
        Checks if :py:class:`~configuration.Config.config_file` exists and if it has a one of the
        :py:class:`~configuration.Config.valid_file_extensions`. 
        """
        self.config_file = self.config_file.replace(
            "~", str(Path.home())
        )
        if not Path(self.config_file).is_file():
            self.errors.append(f"File {self.config_file} does not exist.")
            return False

        filename, file_extension = os.path.splitext(self.config_file)
        self.file_extension = file_extension

        if self.file_extension not in self.valid_file_extensions:
            self.errors.append("Valid configuration file extension are: {}".
                               format(', '.join([*self.valid_file_extensions])))
            return False

        return True

    def parse(self) -> bool:
        """
        Parses the configuration from :py:class:`~configuration.Config.config_file`
        into :py:class:`~configuration.Config.config_object`.
        Returns ``True`` if successful, ``False`` otherwise.

        Todo:
            * either remove ``.toml`` or implement it
        """

        try:
            if self.file_extension == ".toml":
                f = open(self.config_file, "rb")
                self.config_object = tomllib.load(f)
            else:
                f = open(self.config_file, "r")
                self.config_object = yaml.safe_load(f)

            f.close()
        except Exception as e:
            self.errors.append(e)
            return False

        return True

    def check_required_keys(self) -> bool:
        """
        Todo:
            * needs implementation
        """

    def return_config(self) -> dict:
        """
        Returns :py:class:`~configuration.Config.config_object`.
        """

        return self.config_object
