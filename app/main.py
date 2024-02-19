from typing import Union
from fastapi import FastAPI, File, UploadFile
from app.controller.recognition import Recognition

# import os
# os.environ["CUDA_VISIBLE_DEVICES"]=""
# os.environ["TF_ENABLE_ONEDNN_OPTS"]="0"

app = FastAPI(title='Api Face Recognition', debug=True)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/recognize/{no_pensiun}")
def recognize(no_pensiun:str, method: str, file: UploadFile):
    data = Recognition()
    return data.processFaceRecognition(no_pensiun, file, method)

@app.post("/comparing2face")
def comparison(img1: UploadFile, img2: UploadFile, method: str):
    data = Recognition()
    return data.compareTwoFace(img1, img2, method)

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
