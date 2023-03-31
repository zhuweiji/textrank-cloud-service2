import logging
from enum import Enum

from aio_pika.abc import AbstractIncomingMessage
from cloud_worker.constants import RABBITMQ_JOB_QUEUE_NAME, RABBITMQ_RESULT_QUEUE_NAME
from cloud_worker.imagerank_module.image_transcribe import ImageInterrogator
from cloud_worker.services.connection_handlers import RabbitMQHandler
from cloud_worker.textrank_module.textrank import TextRank, TextRankKeywordResult

log = logging.getLogger(__name__)

class TaskType(Enum):
    KEYWORD_EXTRACTION = 'KEYWORD_EXTRACTION'
    IMAGE_TRANSCRIPTION = 'IMAGE_TRANSCRIPTION'

class TaskProcesor:
    work_queue_provider = RabbitMQHandler
    
    @classmethod
    async def process_task(cls, message: AbstractIncomingMessage):
        headers = message.headers
        
        task_type = headers['task_type']
        task_id = headers['task_id']
        
        log.info(f'processing new {task_type} task')
        
        if task_type == TaskType.KEYWORD_EXTRACTION.value:
            data = message.body.decode()
            
            result =  cls.handle_text_keyword_extraction(data)
            log.info(result)
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, result, {'task_type': TaskType.KEYWORD_EXTRACTION.value, 'task_id':task_id})
            
            
        elif task_type == TaskType.IMAGE_TRANSCRIPTION.value:
            data = message.body.decode()
            result = ImageInterrogator.convert_image_to_text(data)
            log.warning(result)
            log.warning('image recongition task - to be implemented')
            
            
            
        else:
            log.warning(f'Could not interpret task: {headers}')
            
    @classmethod
    async def listen_for_incoming_tasks(cls):
        await cls.work_queue_provider.listen(RABBITMQ_JOB_QUEUE_NAME, on_message_handler=TaskProcesor.process_task)
    
    @classmethod
    def handle_text_keyword_extraction(cls, request_text):
        result = TextRank.keyword_extraction__undirected(request_text)
            
        result_as_str = [str(i) for i in result]
        result_as_str = ", ".join(result_as_str)
        
        return result_as_str
