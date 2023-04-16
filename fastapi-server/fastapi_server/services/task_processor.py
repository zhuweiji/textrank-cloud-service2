
import logging
import pickle
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from typing import BinaryIO, List, Union

from aio_pika.abc import AbstractIncomingMessage
from fastapi_server.constants import RABBITMQ_JOB_QUEUE_NAME
from fastapi_server.entities.POST_bodies import (
    Image_Rank_with_Sentences,
    Sentence_Extraction_Request,
    Text_Transcribe_Request,
)
from fastapi_server.entities.responses import (
    endpoint_not_implemented_response,
    text_response,
)
from fastapi_server.services.connection_handlers import RabbitMQHandler
from ulid import ulid

log = logging.getLogger(__name__)


class TaskType(Enum):
    KEYWORD_EXTRACTION = 'KEYWORD_EXTRACTION'
    IMAGE_TRANSCRIPTION = 'IMAGE_TRANSCRIPTION'
    SENTENCE_EXTRACTION = 'SENTENCE_EXTRACTION'
    SENTENCE_EXTRACTION_LIST = 'SENTENCE_EXTRACTION_LIST'
    
    
@dataclass
class JobSpecification:
    task_type: TaskType
    data: Union[str, BinaryIO, tempfile.SpooledTemporaryFile, tempfile._TemporaryFileWrapper, None]
    pickled_data: Union[bytes, None] = None
    other_information: dict = field(default_factory=lambda: {})
    
    task_id: str = field(default_factory=lambda: ulid())
    
    
class JobProcessor:
    completed_jobs = {}
    
    @classmethod
    async def create_image_rank_job(cls, file: Union[BinaryIO, tempfile.SpooledTemporaryFile, tempfile._TemporaryFileWrapper], codec: str):
        job = JobSpecification(
            task_type=TaskType.IMAGE_TRANSCRIPTION,
            data=file,
            other_information={'codec': codec}
            )
        
        job_start_result = await cls.publish_new_job(job)
        return job if job_start_result else False
            
    @classmethod
    async def create_keyword_extraction_job(cls, request_body: Text_Transcribe_Request):
        request_text = request_body.text
        job = JobSpecification(
            task_type=TaskType.KEYWORD_EXTRACTION,
            data=request_text,)
        
        job_start_result = await cls.publish_new_job(job)
        return job if job_start_result else False
    
    @classmethod
    async def create_sentence_extraction_job(cls, request_body: Sentence_Extraction_Request):
        request_text = request_body.text
        job = JobSpecification(
            task_type=TaskType.SENTENCE_EXTRACTION,
            data=request_text,
            )
        
        job_start_result = await cls.publish_new_job(job)
        return job if job_start_result else False
    
    @classmethod
    async def create_image_rank_w_sentences_job(cls, request_body: Image_Rank_with_Sentences):
        request_text = request_body.delimited_text
        job = JobSpecification(
            task_type=TaskType.SENTENCE_EXTRACTION_LIST,
            data=request_text,
            )
        
        job_start_result = await cls.publish_new_job(job)
        return job if job_start_result else False
        
                
    @classmethod 
    async def publish_new_job(cls, job: JobSpecification):
        if job.data and job.pickled_data: raise ValueError("currently supports only job.data or job.pickled_data")
        headers = {'task_type': job.task_type.value, 'task_id':job.task_id, 'other_info': job.other_information}
        
        if job.pickled_data: headers['pickled'] = True
        data = job.data or job.pickled_data
        if not data: raise ValueError
        
        log.info(headers)
        try:
            await RabbitMQHandler.publish(RABBITMQ_JOB_QUEUE_NAME, data, headers)
            return True
        except Exception:
            log.exception(f'Error publishing new job: {job}')
            return False
        
    @classmethod
    def handle_new_result(cls, message: AbstractIncomingMessage):
        headers = message.headers
    
        task_type = headers['task_type']
        task_id   = headers['task_id']
        pickled   = headers.get('pickled', None)
        
        data = message.body.decode() if not pickled else pickle.loads(message.body) 
        
        
        if task_type in [i.value for i in TaskType]:
            job = JobSpecification(
                task_type=str(task_type), # type: ignore
                data=data,
                task_id=str(task_id)
                )
            cls.completed_jobs[task_id] = job
        else:
            raise NotImplementedError

    
    @classmethod
    def check_job_status(cls, task_id):
        # log.info(cls.completed_jobs)
        return cls.completed_jobs.get(task_id,None)
