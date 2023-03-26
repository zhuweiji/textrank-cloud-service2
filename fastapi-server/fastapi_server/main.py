import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi_server import get_logger
from fastapi_server.entities.responses import healthcheck_response
from fastapi_server.services.imagerank_service import image_rank_service
from fastapi_server.services.textrank_service import text_rank_service

log = get_logger(__name__)

app = FastAPI(
    title="TextRank Backend",
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root_endpoint():
    return healthcheck_response()

@app.route('/text_rank', methods=["POST"])
def text_rank_route(text: str):
    return text_rank_service(text)

@app.post('/image_transcribe')
async def image_transcribe_route(image: UploadFile= File()):
    file_suffix_is_img = (image.filename or "").split('.')[-1] in ('jpg','png')
    if not file_suffix_is_img:
        raise HTTPException(400, 'The file must be either a .jpg or .png file')
    
    file_obj = image.file
    return image_rank_service(file_obj)


