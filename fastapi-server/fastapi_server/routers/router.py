import asyncio
import logging
import shutil
import tempfile
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
    jobs_created_response,
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
async def image_transcribe_route(images: list[UploadFile]):
    
    file_suffix_is_img = lambda image: image.filename.split('.')[-1] in ('jpg','png')
    if not [file_suffix_is_img(i) for i in images]:
        raise HTTPException(400, 'The file must be either a .jpg or .png file')
    
    file_objs = [image.file for image in images]
    
    # create a copy of the files because otherwise we get a IOError file closed 
    file_copies = [tempfile.NamedTemporaryFile(delete=True) for _ in file_objs]
    for copy,file in zip(file_copies, file_objs):
        copy.write(file.read())
    
    jobs = [JobProcessor.create_image_rank_job(i) for i in file_copies]
    result = await asyncio.gather(*jobs)
    
    successfully_started_jobs = [i for i in result if i]
    unsuccessful_jobs         = [i for i in result if not i]
    
    if unsuccessful_jobs:
        log.warning(f'unable to start some image transcribe jobs: {unsuccessful_jobs}')
    
    if jobs:
        return jobs_created_response(successfully_started_jobs)
    else:
        return text_response(f'unable to create job. please try again')
    

@router.get('/check_task_result')
async def get_job_result_route(task_id: str):
    while True:
        job = JobProcessor.check_job_status(task_id)
        if job:
            return text_response(job.data)
        else:
            await asyncio.sleep(1)
            
        
