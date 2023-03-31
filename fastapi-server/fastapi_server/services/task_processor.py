
import logging
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from typing import BinaryIO, Union

from aio_pika.abc import AbstractIncomingMessage
from fastapi_server.constants import RABBITMQ_JOB_QUEUE_NAME
from fastapi_server.entities.POST_bodies import Text_Transcribe_Request
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
    
    
@dataclass
class JobSpecification:
    task_type: TaskType
    data: Union[str, BinaryIO, tempfile.SpooledTemporaryFile, tempfile._TemporaryFileWrapper]
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
    async def create_text_rank_job(cls, request_body: Text_Transcribe_Request):
        request_text = request_body.text
        job = JobSpecification(
            task_type=TaskType.KEYWORD_EXTRACTION,
            data=request_text,)
        
        job_start_result = await cls.publish_new_job(job)
        return job if job_start_result else False
        
    @classmethod 
    async def publish_new_job(cls, job: JobSpecification):
        headers = {'task_type': job.task_type.value, 'task_id':job.task_id, 'other_info': job.other_information}
        log.info(headers)
        try:
            await RabbitMQHandler.publish(RABBITMQ_JOB_QUEUE_NAME, job.data, headers)
            return True
        except Exception:
            log.exception(f'Error publishing new job: {job}')
            return False
        
    @classmethod
    def handle_new_result(cls, message: AbstractIncomingMessage):
        headers = message.headers
    
        task_type = headers['task_type']
        task_id   = headers['task_id']
        
        if task_type == TaskType.KEYWORD_EXTRACTION.value:
            job = JobSpecification(
                task_type=TaskType.KEYWORD_EXTRACTION,
                data=message.body.decode(),
                task_id=str(task_id)
                )
            cls.completed_jobs[task_id] = job
        elif task_type == TaskType.IMAGE_TRANSCRIPTION.value:
            log.info(message)
            log.info(message.body.decode())
            
            job = JobSpecification(
                task_type=TaskType.IMAGE_TRANSCRIPTION,
                data=message.body.decode(),
                task_id=str(task_id)
                )
            cls.completed_jobs[task_id] = job
        else:
            raise NotImplementedError

    
    @classmethod
    def check_job_status(cls, task_id):
        # log.info(cls.completed_jobs)
        return cls.completed_jobs.get(task_id,None)
