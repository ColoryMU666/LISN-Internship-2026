import requests
import os
import subprocess
import platform
import sys

def request(lockfile):

    try:
        url = f"{sys.argv[1]}upload/"
    except:
        raise IndexError("The link to the server was not given")


    fileinfo = open("/etc/hostname")
    info = fileinfo.read()
    fileinfo.close()

    machine = platform.machine()
    platform_map = {
        "x86_64": "x86_64-unknown-linux-gnu",
        "aarch64": "aarch64-unknown-linux-gnu",
        "arm64": "aarch64-unknown-linux-gnu",
    }
    target_platform = platform_map.get(machine, "x86_64-unknown-linux-gnu")

    response = requests.post(url, files=lockfile, data={
             "hostname": info,
            "platform": target_platform,
            "python_version": "3.14"
        })
    if response.status_code != 200:
        raise ValueError(f"Server rejected the request ({response.status_code}): {response.text}")

    print(response.text)

    subprocess.run("uv sync --offline", shell=True, check=True)

if __name__ == "__main__":
    pass