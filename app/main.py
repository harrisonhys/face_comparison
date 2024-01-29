from typing import Union
from fastapi import FastAPI, File, UploadFile
from app.controller.recognition import Recognition
import logging

app = FastAPI(title='Api Face Recognition', debug=True)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/recognize/{no_pensiun}")
def recognize(no_pensiun:str, file: UploadFile):
    data = Recognition()
    return data.processFaceRecognition(no_pensiun, file)