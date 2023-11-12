import os
import sys
import re
from getpass import getpass
from pathlib import Path
import base64
from Crypto.Cipher import AES
# conquers libraries
from constants import Constants as Const

class MasterkeyError(Exception):
    pass

class CredentialsError(Exception):
    pass

class CryptoError(Exception):
    pass

class Credentials:
    """
    A class to check, retrieve, add, encrypt and decrypt credentials necessary
    to connect to a switch.

    Attributes:
        credentials_file (str)
            Relative or absolute path to a credentials file that is to be used.
            It is passed via the command line flag ``--credentials``.
            If no path is passed, the default credentials file `credentials` in 
            :py:class:`~constants.Const.CHOME` is used.
        file_handle (file)
            File handle used to read from and write to credentials file.
        master_key (str)
            Used to encrypt and decrypt passwords.
            Can have a lenth of **32** characters max.
            Can be passed via the **-m** flag and can be the actual master key
            (discouraged) or a relative/absolute path to a file containing the
            master key. If not provided
            :py:func:`~cscredentials.Credentials.__init__` will ask for it
            using the python module `getpass <https://docs.python.org/3/library/getpass.html>`_.

    """

    def __init__(self, credentials_file, master_key=None) -> None:
        self.credentials_file = credentials_file.replace("~", str(Path.home()))
        self.file_handle = None

        if master_key is not None:
            if Path(
                master_key.replace(
                    "~", str(Path.home())
                )
            ).is_file():
                with open(master_key, "r", encoding="utf-8") as mfile:
                    master_key = mfile.readline().rstrip()

        try:
            self.check_credentials_file_exists()
        except CredentialsError as e:
            print(e)
            sys.exit(1)

        if master_key is None:
            for i in range(0,3):                        # ask three times max.
                try1 = getpass(prompt="Master key: ")
                try2 = getpass(prompt="Please repeat: ")

                if try1 == try2:
                    master_key = try1
                    break

                if i == 2:
                    print("Keys do not match, giving up.")
                    sys.exit(1)
                else:
                    print("No match, try again.")

        # Master key of max length of 32 characters.
        if len(master_key) > 32:
            raise CredentialsError("Master key can only be 32 characters long.")

        self.master_key = master_key.encode().rjust(32)

    def check_credentials_file_exists(self) -> None:
        """
        Checks if the passed credentials file exists.
        Uses default credentials file in
        :py:class:`~constants.Const.CHOME_ABS_PATH`
        """
        if not Path(self.credentials_file).is_file():
            Const.set_abs_path()
            print(f"Credentials file {self.credentials_file} does not exist \
                  using {Const.CHOME}credentials ...")
            self.credentials_file = f"{Const.CHOME_ABS_PATH}/credentials"

    def encrypt_pass(self, credentials) -> str:
        """
        Encrypt password with AES using
        :py:class:`~credentials.Credentials.master_key`
        and encode it using base64.
        """

        cipher = AES.new(self.master_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(credentials["pass"].encode())

        encrypted = b''
        for x in (cipher.nonce, tag, ciphertext):
            encrypted += x

        return base64.b64encode(encrypted).decode()

    def decrypt_pass(self, credentials) -> str:
        """
        Decode base64 string and decrypt using
        :py:class:`~credentials.Credentials.master_key`
        """

        decoded = base64.b64decode(credentials["encrypted_pass"])

        nonce = decoded[0:16]
        tag = decoded[16:32]
        ciphertext = decoded[32:len(decoded)]

        cipher = AES.new(self.master_key, AES.MODE_EAX, nonce)
        try:
            data = cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            raise CryptoError(e) from e

        return "{}".format(data.decode())

    def add_entry(self, credentials) -> None:
        """
        Writes entry to :py:class:`~credentials.Credentials.credentials_file`
        """

        credentials["encrypted_pass"] = self.encrypt_pass(credentials)

        with open(self.credentials_file, "a", encoding="utf-8") \
                as self.file_handle:
            self.file_handle.write(
                "{user}@{host}:{encrypted_pass}\n".format(**credentials)
            )

    def override_entry(self, credentials) -> None:
        """
        Override matching credentials entry with the new one.
        """

        credentials["encrypted_pass"] = self.encrypt_pass(credentials)

        with open(self.credentials_file, "r", encoding="utf-8") \
                as self.file_handle:
            lines = self.file_handle.readlines()

        with open(self.credentials_file, "w", encoding="utf-8") \
            as self.file_handle:

            for l in lines:
                if l.split(":")[0].split("@")[1] == credentials["host"]:
                    self.file_handle.write(
                        "{user}@{host}:{encrypted_pass}\n".format(**credentials)
                    )
                else:
                    self.file_handle.write(l)

    def check_entry_exists(self, host) -> str:
        """
        Returns `user@host` of the match, if found,
        an empty string otherwise.
        """
        with open(self.credentials_file, "r", encoding="utf-8") as \
                self.file_handle:
            lines = self.file_handle.readlines()

        for l in lines:
            if host == l.split(":")[0].split("@")[1]:
                return l.split(":")[0]

        return ""

    def checks_add_entry(self, credentials=None) -> bool:
        """
        Asks for
            * host
            * user
            * password

        Asks whether to override, if entry exists.
        Asks three times to repeat at most, if passwords do not match.
        Aborts if override is denied, otherwise calls
        :py:class:`~credentials.Credentials.override_entry()`
        or
        :py:class:`~credentials.Credentials.add_entry()`
        """

        if credentials is None:

            while True:
                credentials = {
                    "host": None,
                    "user": None,
                    "pass": None,
                }

                credentials["host"] = input("Hostname: ")
                credentials["user"] = input(
                    "Username for {host}: ".format(**credentials)
                )

                # Ask three times at most.
                for i in range(0,3):
                    try1 = getpass(
                        prompt="Password for {user}@{host}:".format(
                            **credentials
                        )
                    )
                    try2 = getpass(prompt="Repeat: ")

                    if try1 == try2:
                        credentials["pass"] = try1
                        break

                    if i == 2:
                        print("Passwords do not match, giving up.")
                        sys.exit(1)
                    else:
                        print("Passwords do not match, try again.")

                # Ask if everything's ok.
                print("{user}@{host}".format(**credentials))
                print("Does this seem ok? [Y/n] ", end="")

                yn = input()

                # Exit while loop if ok.
                if yn == "" or yn.lower() == "y":
                    break

        # Check if entry already exists.
        if(check := self.check_entry_exists("{host}".format(**credentials))):
            print(f"An entry already exists ({check}). Overwrite? [y/N] ",
                  end="")
            yn = input()

            if yn.lower() != "y":
                print("Entry not added.")
                return False
            # Add entry.
            try:
                self.override_entry(credentials)
            # Can be PermissionError or FileNotFoundError
            except Exception as e:
                print(e)
                sys.exit(1)
        # Add entry.
        else:
            try:
                self.add_entry(credentials)
            except Exception as e:
                print(e)
                sys.exit(1)

        print("Entry added.")

        return True

    def return_credentials(self, host) -> dict:
        """
        Returns credentials dictionary if entry found

            .. code-block:: python
                :caption: Something like this 

                {
                    "user": "username",
                    "host": "hostname",
                    "encrypted_pass": "base64 string of encrypted password",
                    "pass": "plain text password"
                }

        Returns empty dictionary otherwise.
        """

        with open(self.credentials_file, "r", encoding="utf-8") as \
                self.file_handle:
            lines = self.file_handle.readlines()

        for l in lines:
            up = l.split(":")
            uh = up[0].split("@")

            # try to match when wildcard found.
            regex = None
            if "*" in uh[1]:
                regex = re.compile(uh[1])

            if host == uh[1] or (regex is not None and regex.match(host)):
                credentials = {
                    "user": uh[0],
                    "host": host,
                    "encrypted_pass": up[1].rstrip()
                }

                try:
                    credentials["pass"] = self.decrypt_pass(credentials)
                except CryptoError as e:
                    print(e)
                    print(
                        "Probably the master key is not correct or the path" + 
                        " (if passed)" +
                        " does not exist."
                    )
                    sys.exit(1)

                return credentials

        return {}
