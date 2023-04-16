import io
import logging
import pickle
from enum import Enum

from aio_pika.abc import AbstractIncomingMessage
from cloud_worker.constants import RABBITMQ_JOB_QUEUE_NAME, RABBITMQ_RESULT_QUEUE_NAME
from cloud_worker.imagerank_module.image_transcribe import ImageInterrogator
from cloud_worker.services.connection_handlers import RabbitMQHandler
from cloud_worker.textrank_module.textrank import TextRank

log = logging.getLogger(__name__)
from PIL import Image


class TaskType(Enum):
    KEYWORD_EXTRACTION  = 'KEYWORD_EXTRACTION'
    IMAGE_TRANSCRIPTION = 'IMAGE_TRANSCRIPTION'
    SENTENCE_EXTRACTION = 'SENTENCE_EXTRACTION'
    SENTENCE_EXTRACTION_LIST = 'SENTENCE_EXTRACTION_LIST'
    

class TaskProcesor:
    work_queue_provider = RabbitMQHandler
    job_handler         = TextRank()
    
    @classmethod
    async def process_task(cls, message: AbstractIncomingMessage):
        headers = message.headers
        
        task_type = headers['task_type']
        task_id = headers['task_id']
        pickled = headers.get('pickled',None)
        other_info:dict = headers['other_info'] # type: ignore
        
        log.info(f'processing new {task_type} task')
        
        if task_type == TaskType.KEYWORD_EXTRACTION.value:
            data = message.body.decode() if not pickled else pickle.loads(message.body)
            
            result =  cls.job_handler.keyword_extraction__undirected(data)
            encoded_data = pickle.dumps(result)
            
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, encoded_data, 
                                          {'task_type': TaskType.KEYWORD_EXTRACTION.value,
                                           'task_id':task_id,
                                           'pickled': True})
            
        elif task_type == TaskType.IMAGE_TRANSCRIPTION.value:
            image_data = message.body
            codec = other_info['codec']
            image_obj = io.BytesIO(image_data)
            
            result = ImageInterrogator.convert_image_to_text(image_obj)
            if not result:
                log.warning('No result from image transcription')
                return
            
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, result, {'task_type': TaskType.IMAGE_TRANSCRIPTION.value, 'task_id':task_id})
            
        elif task_type == TaskType.SENTENCE_EXTRACTION.value:
            data = message.body.decode()
            result = cls.job_handler.sentence_extraction__undirected(data)
            encoded_data = pickle.dumps(result)
            
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, encoded_data, 
                                          {'task_type': TaskType.SENTENCE_EXTRACTION.value,
                                           'task_id':task_id,
                                           'pickled': True})
            
        elif task_type == TaskType.SENTENCE_EXTRACTION_LIST.value:
            data = message.body.decode()
            data = data.split('|')
            result = cls.job_handler.sentence_extraction__undirected(data)
            encoded_data = pickle.dumps(result)
            
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, encoded_data, 
                                        {'task_type': TaskType.SENTENCE_EXTRACTION_LIST.value,
                                           'task_id':task_id,
                                           'pickled': True})
            
        else:
            log.warning(f'Could not interpret task: {headers}')
            
        
            
        log.info(f'completed {task_type} task')
        
        
            
    @classmethod
    async def listen_for_incoming_tasks(cls):
        try:
            await cls.work_queue_provider.listen(RABBITMQ_JOB_QUEUE_NAME, on_message_handler=TaskProcesor.process_task)
        except Exception:
            log.exception('unable to connect to work queue')
            exit(-1)
            
    
