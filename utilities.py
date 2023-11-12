"""
Utilities used in conquers
"""
import sys
import os
from pathlib import Path
import base64
import subprocess
import struct
from collector import Collector

def decide_pub_key_method(file_path, device_type) -> None:
    """
    Decide which method to use and execute.
    """

    if device_type == "cisco_ios":
        do_convert_pubkey_cisco_ios(file_path)
    elif device_type == "huawei":
        do_convert_pubkey_huawei(file_path)
    else:
        Collector.print_error(f"Device type {device_type} is unknown.")
        sys.exit(1)

def do_convert_pubkey_cisco_ios(file_path) -> None:
    """
    Exports openssh public key in cisco_ios format.
    """

    file_path = Path(file_path.replace("~", str(Path.home())))

    max_length = 72

    if not Path(file_path).is_file():
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    file_path = os.path.abspath(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            while True:
                data = fh.read(max_length)
                if data == "":
                    break

                print(data.rstrip())
    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)

def do_convert_pubkey_huawei(file_path) -> None:
    """
    Exports public key in huawei format.
    """

    ssh_keygen_installed = None

    if sys.platform == "linux" or \
       sys.platform == "darwin":
        ssh_keygen_installed = subprocess.run(
            "which ssh-keygen".split(" "),
            stdout=subprocess.PIPE
        )
    elif sys.platform == "win32":
        ssh_keygen_installed = subprocess.run(
            "where.exe ssh-keygen".split(" "),
            stdout=subprocess.PIPE
        )

    if ssh_keygen_installed.returncode != 0:
        print("You need ssh-keygen to be installed and in your path.")
        sys.exit(1)

    file_path = Path(file_path.replace("~", str(Path.home())))

    if not Path(file_path).is_file():
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    file_path = os.path.abspath(file_path)

    try:
        pem_key_data = subprocess.run(
            f"ssh-keygen -e -m pem -f {file_path}".split(" "),
            stdout=subprocess.PIPE
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    if pem_key_data.returncode != 0:
        print("Something went wrong converting the key.")
        print(pem_key_data)
        sys.exit(1)

    key_d = pem_key_data.stdout.decode("utf-8")

    # Remove lines BEGIN RSA PUBLIC KEY and END RSA PUBLIC KEY
    key = ''.join([f"{k}\n" for k in key_d.splitlines() if "---" not in k])

    try:
        bin_data = base64.b64decode(key)
    except Exception as e:
        print(e)
        sys.exit(1)

    c = 0
    c_four = 0

    while True:
        b2_chunk = bin_data[c:c+2]

        c += 2
        # Read 2 byte chunks.
        # Failing means we're done.
        try:
            # >H unsigned big-endian
            print(
                hex(
                    struct.unpack(
                        '>H', b2_chunk
                    )[0]
                ).replace(
                    "0x", ""            # remove string "0x"
                ).upper().zfill(4),     # pad with zeroes to 4 bytes
                end=""
            )

            c_four += 2

            if c_four % 32 == 0:
                print("")               # break line
            elif c_four % 4 == 0:
                print(" ", end="")      # print space after chunk

        except Exception as e:
            break

    print("")

    sys.exit(0)
