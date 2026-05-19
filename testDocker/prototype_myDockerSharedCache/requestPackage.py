import requests
import os
import subprocess
import platform
import sys

subprocess.run('uv lock', shell=True)
subprocess.run('uv export -q -o pylock.toml', shell=True)

try:
    url = f"http://{sys.argv[1]}:8000/upload/"
    urlInfo = f"http://{sys.argv[1]}:8000/info/"
except:
    raise IndexError("The link to the server was not given")


fileinfo = open("/etc/hostname")
info = fileinfo.read()
fileinfo.close()

if not os.path.isfile("info.txt"):
    file = open("info.txt", "a")
    file.write(info)
    file.close()

machine = platform.machine()
platform_map = {
    "x86_64": "x86_64-unknown-linux-gnu",
    "aarch64": "aarch64-unknown-linux-gnu",
    "arm64": "aarch64-unknown-linux-gnu",
}
target_platform = platform_map.get(machine, "x86_64-unknown-linux-gnu")

files = {'file': open('pylock.toml', 'r')}
infos = {'file': open('info.txt', 'r')}

requests.post(urlInfo, files=infos)
response = requests.post(url, files=files, data={
    "platform": target_platform,
    "python_version": "3.14"
})

print(response.text)

# Le cache est déjà monté, on peut directement sync
subprocess.run("uv sync --offline", shell=True, check=True)