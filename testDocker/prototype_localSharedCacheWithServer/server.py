from fastapi import FastAPI, UploadFile, HTTPException
import shutil
import os
import subprocess

app = FastAPI()
info = ["a"]

# Configuration des répertoires
BASE_DIR = os.getcwd()

@app.post("/info/")
async def set_info(file : UploadFile):
    content = await file.read()
    info[0] = content.decode('utf-8').strip()
    return

@app.get("/info/")
async def get_info():
    return {"message" : info[0]}

@app.post("/upload/")
async def sync_pylock(file: UploadFile):
    # sauvegarder le fichier reçu
    local_file_path = os.path.join(BASE_DIR, file.filename)

    try:
        #Enregistrement physique du fichier sur le serveur
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        subprocess.run('uv pip sync pylock.toml', shell=True) # Synchroniser les dépendances avec pylock.toml
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    subprocess.run(f'echo {info[0]}', shell=True)
    subprocess.run(f"sudo docker cp ~/.cache/uv {info[0]}:/tmp/uv_cache", shell=True)
    return "Done"