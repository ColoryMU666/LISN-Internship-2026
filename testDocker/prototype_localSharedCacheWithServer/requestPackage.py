import requests
import os
import sys
import subprocess
from pathlib import Path

subprocess.run('uv lock', shell=True) # Mettre uv lock
subprocess.run('uv export -q -o pylock.toml', shell=True)
url = "http://host.docker.internal:8000/upload/"
urlInfo = "http://host.docker.internal:8000/info/"

fileinfo = open("/etc/hostname")
info = fileinfo.read()
fileinfo.close()

if not os.path.isfile("info.txt"):
    file = open("info.txt", "a")
    file.write(info)
    file.close()

files={'file': open('pylock.toml','r')}
infos = {'file' : open('info.txt', 'r')}

requests.post(urlInfo, files=infos)
response = requests.post(url, files=files)
print(response.text)


ADMIN_CACHE = Path("/tmp/uv")
USER_CACHE = Path("/root/.cache/uv")

def lier_cache(src_root, dest_root):


    for src_file in src_root.rglob("*"):
        
        relative_path = src_file.relative_to(src_root)

        # On ignore les dossiers qui vont être créés après et les .lock
        if src_file.is_dir() or src_file.name == ".lock":
            continue
        
        # Chemin cible dans USER_CACHE
        dest_file = dest_root / relative_path

        if not dest_file.exists():
            try:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.symlink_to(src_file)
                print(f"Lien créé : {relative_path}")
            except Exception as e:
                continue
    subprocess.run(f"rm -rf {src_root}")
    


lier_cache(ADMIN_CACHE, USER_CACHE)
