import socket
from typing import Union
from fastapi import FastAPI, File, UploadFile
from app.controller.recognition import Recognition
from app.controller.environment_config import EnvironmentConfig

# import os
# os.environ["CUDA_VISIBLE_DEVICES"]=""
# os.environ["TF_ENABLE_ONEDNN_OPTS"]="0"

app         = FastAPI(title='Api Face Recognition', debug=True)
db_host     = EnvironmentConfig.get_env_value('DB_HOST', default='localhost')
db_port     = EnvironmentConfig.get_env_value('DB_PORT', default=5432)

@app.get("/")
def read_root():
    hostname    = socket.gethostname()
    ip_address  = socket.gethostbyname(hostname)
    return {"Host" : db_host, "Port": db_port, "ip_address": ip_address}

@app.post("/recognize/{no_pensiun}")
def recognize(no_pensiun:str, method: str, file: UploadFile):
    data = Recognition()
    return data.processFaceRecognition(no_pensiun, file, method)

@app.post("/photo-info")
def comparison(img: UploadFile):
    data = Recognition()
    return data.photoAnalyser(img)

@app.post("/comparing2face")
def comparison(img1: UploadFile, img2: UploadFile, method: str):
    data = Recognition()
    return data.compareTwoFace(img1, img2, method)

@app.post("/comparing-from-db")
def comparison(current: str, previous: str, method: str):
    data = Recognition()
    return data.comparingFromDatabase(current, previous, method)

@app.get("/log")
def getLog():
    data = Recognition()
    return data.getLog()

@app.get("/log/{tanggal}")
def getDetailLog(tanggal:str):
    data = Recognition()
    return data.geDetailLog(tanggal)

@app.post("/log/clear")
def clearLog(tanggal:str):
    data = Recognition()
    return data.clearLog(tanggal)

@app.post("/log/clear-all")
def clearLogAll():
    data = Recognition()
    return data.clearAllLog()
