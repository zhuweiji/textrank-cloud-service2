import logging

from aio_pika.abc import AbstractIncomingMessage
from cloud_worker.constants import RABBITMQ_JOB_QUEUE_NAME, RABBITMQ_RESULT_QUEUE_NAME
from cloud_worker.services.connection_handlers import RabbitMQHandler
from cloud_worker.textrank_module.textrank import TextRank, TextRankKeywordResult

log = logging.getLogger(__name__)

KEYWORD_EXTRACTION = 'KEYWORD_EXTRACTION'


class TaskProcesor:
    @classmethod
    async def process_task(cls, message: AbstractIncomingMessage):
        headers = message.headers
        
        task_type = headers['task_type']
        task_id = headers['task_id']
        
        log.info(f'processing new {task_type} task')
        
        if task_type == KEYWORD_EXTRACTION:
            data = message.body.decode()
            
            result =  cls.handle_text_keyword_extraction(data)
            log.info(result)
            await RabbitMQHandler.publish(RABBITMQ_RESULT_QUEUE_NAME, result, {'task_type': KEYWORD_EXTRACTION, 'task_id':task_id})
        else:
            log.warning(f'Could not interpret task: {headers}')
            
    @classmethod
    async def listen_for_incoming_tasks(cls):
        await RabbitMQHandler.listen(RABBITMQ_JOB_QUEUE_NAME, on_message_handler=TaskProcesor.process_task)
    
    @classmethod
    def handle_text_keyword_extraction(cls, request_text):
        result = TextRank.keyword_extraction__undirected(request_text)
            
        result_as_str = [str(i) for i in result]
        result_as_str = ", ".join(result_as_str)
        
        return result_as_str
