import asyncio
import logging
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
    job_created_response,
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
    job = await JobProcessor.create_text_rank_job(body)
    if job:
        return job_created_response(job.task_id)
    else:
        raise HTTPException(status_code=500, detail='an error occured while creating the task')

    

@router.post('/image_transcribe')
async def image_transcribe_route(image: UploadFile= File()):
    file_suffix_is_img = (image.filename or "").split('.')[-1] in ('jpg','png')
    if not file_suffix_is_img:
        raise HTTPException(400, 'The file must be either a .jpg or .png file')
    
    file_obj = image.file
    job = await JobProcessor.create_image_rank_job(file_obj)
    if job:
        return text_response(f'created new job with id: {job.task_id}')
    else:
        return text_response(f'unable to create job. please try again')
    

@router.get('/check_task_result')
async def get_job_result_route(task_id: str):
    while True:
        job = JobProcessor.check_job_status(task_id)
        log.info(job)
        if job:
            return text_response(job.data)
        else:
            await asyncio.sleep(1)
            
        
