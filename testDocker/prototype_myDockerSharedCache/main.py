import subprocess
import os
import requestPackage
from fastapi import FastAPI, HTTPException

VENV_LOCATION = "/tmp/venv/"
BASE_DIR = os.getcwd()

def main():
    subprocess.run(f"uv init {VENV_LOCATION}", shell=True)
    os.chdir(f"{VENV_LOCATION}")
    subprocess.run("ls", shell=True)
    packages = []
    stop = False
    while not stop:
        requestedPackage = input("Please enter the name of the requested package or leave blank to exit :\n")
        if requestedPackage == "":
            stop = True
        else:
            try:
                subprocess.run(f"uv add {requestedPackage}", shell=True)
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode() if e.stderr else "no stderr"
                stdout = e.stdout.decode() if e.stdout else "no stdout"
                print(f"stderr : {stderr}\n stdout : {stdout}")
    subprocess.run("uv lock", shell=True)
    subprocess.run('uv export -q -o pylock.toml', shell=True)
    requestPackage.request(lockfile={'file': open('pylock.toml', 'r')})
    subprocess.run("rm -rf ./*", shell=True)
    os.chdir(f"{BASE_DIR}")

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        subprocess.run("uv lock", shell=True)
        subprocess.run("rm -rf ./*", shell=True)
        os.chdir(f"{BASE_DIR}")
        print("Ending process properly")
    except HTTPException as e:
        subprocess.run("rm -rf ./*", shell=True)
        print(f"Error : {e.detail}")