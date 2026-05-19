import subprocess
import os

VENV_LOCATION = "/tmp/venv/"
BASE_DIR = os.getcwd()

def main():
    subprocess.run(f"uv venv {VENV_LOCATION}", shell=True)
    subprocess.run(f"cd {VENV_LOCATION}", shell=True)
    packages = []
    stop = False
    while not stop:
        requestedPackage = input("Please enter the name of the requested package or leave a blank to exit :\n")
        if requestedPackage == "":
            stop = True
        else:
            try:
                subprocess.run(f"uv add {requestedPackage}", shell=True)
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode() if e.stderr else "no stderr"
                stdout = e.stdout.decode() if e.stdout else "no stdout"
                print(f"stderr : {stderr}\n stdout : {stdout}")
    subprocess.run(f"cd {BASE_DIR}", shell=True)

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        raise KeyboardInterrupt