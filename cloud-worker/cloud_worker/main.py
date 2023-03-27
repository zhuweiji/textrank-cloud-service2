import asyncio

from cloud_worker.constants import RABBITMQ_JOB_QUEUE_NAME
from cloud_worker.services.connection_handlers import RabbitMQHandler
from cloud_worker.services.task_processer import TaskProcesor

tasks = set()

import logging

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

import asyncio

tasks = set()

def run_task(coro):
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)


async def main():
    t = asyncio.create_task(TaskProcesor.listen_for_incoming_tasks())
    tasks.add(t)
    await asyncio.Future()
        
if __name__ == "__main__":
    asyncio.run(main())
    