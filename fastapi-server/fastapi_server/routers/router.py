import asyncio
import logging
import shutil
import tempfile
from dataclasses import dataclass
from typing import List

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi_server.entities.POST_bodies import Text_Transcribe_Request
from fastapi_server.entities.responses import (
    endpoint_not_implemented_response,
    job_completed_response,
    job_created_response,
    job_created_response__multiple,
    text_response,
)
from fastapi_server.services.task_processor import JobProcessor

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)



ROUTE_PREFIX = '/api'

router = APIRouter(
    prefix=ROUTE_PREFIX,
)

@router.post('/text_rank')
async def text_rank_route(body: Text_Transcribe_Request):
    job = await JobProcessor.create_keyword_extraction_job(body)
    if job:
        return job_created_response(job.task_id)
    else:
        raise HTTPException(status_code=500, detail='an error occured while creating the task')

@router.post('/sentence_extraction')
async def sentence_extraction_route(body: Text_Transcribe_Request):
    job = await JobProcessor.create_sentence_extraction_job(body)
    if job:
        return job_created_response(job.task_id)
    else:
        raise HTTPException(status_code=500, detail='an error occured while creating the task')

@router.post('/image_transcribe')
async def image_transcribe_route(images: list[UploadFile]):
    get_file_suffix = lambda image: image.filename.split('.')[-1] 
    
    @dataclass
    class ImageToBeProcessed:
        data: bytes
        codec: str
    
    data = []
    for image in images:
        suffix = get_file_suffix(image)
        if suffix not in ('png','jpg'): raise HTTPException(400, 'The file must be either a .jpg or .png file')
        
        file_data = image.file.read()
        if len(file_data) > 52_428_800: #50mb
            raise HTTPException(status_code=413, detail='Image files cannot be larger than 50mb')
        
        data.append(ImageToBeProcessed(file_data, suffix))
    
    
    jobs = [JobProcessor.create_image_rank_job(i.data, i.codec) for i in data]
    result = await asyncio.gather(*jobs)
    
    successfully_started_jobs = [i.task_id for i in result if i]
    unsuccessful_jobs         = [i for i in result if not i]
    
    log.warning(successfully_started_jobs)
    if unsuccessful_jobs:
        log.warning(f'unable to start some image transcribe jobs: {unsuccessful_jobs}')
    
    if jobs:
        return job_created_response__multiple(successfully_started_jobs)
    else:
        return text_response(f'unable to create job. please try again')
    

@router.get('/check_task_result')
async def get_job_result_route(task_id: str):

    return {
    "task_id": "01GX5FGK5RCPRR6FX6SV4X97WA",
    "result": [
        {
            "id": 3,
            "name": "et",
            "connected": [
                1,
                5,
                4,
                2
            ],
            "score": 4
        },
        {
            "id": 6,
            "name": "aute",
            "connected": [
                4,
                5,
                7,
                8
            ],
            "score": 4
        },
        {
            "id": 9,
            "name": "enim",
            "connected": [
                11,
                8,
                7,
                10
            ],
            "score": 4
        },
        {
            "id": 12,
            "name": "amet",
            "connected": [
                10,
                11,
                13
            ],
            "score": 3
        },
        {
            "id": 0,
            "name": "Qui",
            "connected": [
                2,
                1
            ],
            "score": 2
        },
        {
            "id": 1,
            "name": "irure",
            "connected": [
                3,
                2
            ],
            "score": 1.0
        },
        {
            "id": 2,
            "name": "nisi",
            "connected": [
                4,
                3,
                1,
                0
            ],
            "score": 1.0
        },
        {
            "id": 4,
            "name": "veniam",
            "connected": [
                6,
                5,
                3,
                2
            ],
            "score": 1.0
        },
        {
            "id": 5,
            "name": "eu",
            "connected": [
                4,
                6,
                3,
                7
            ],
            "score": 1.0
        },
        {
            "id": 7,
            "name": "ex",
            "connected": [
                9,
                6,
                5,
                8
            ],
            "score": 1.0
        },
        {
            "id": 8,
            "name": "culpa",
            "connected": [
                10,
                6,
                9,
                7
            ],
            "score": 1.0
        },
        {
            "id": 10,
            "name": "ea",
            "connected": [
                12,
                11,
                9,
                8
            ],
            "score": 1.0
        },
        {
            "id": 11,
            "name": "ad",
            "connected": [
                10,
                13,
                12,
                9
            ],
            "score": 1.0
        },
        {
            "id": 13,
            "name": "esse.",
            "connected": [
                12,
                11
            ],
            "score": 1.0
        }
    ]
    }

    # while True:
    #     job = JobProcessor.check_job_status(task_id)
    #     if job:
    #         log.info(job_completed_response(task_id=job.task_id, result=job.data))
    #         return job_completed_response(task_id=job.task_id, result=job.data)
    #     else:
    #         await asyncio.sleep(1)
            
        
