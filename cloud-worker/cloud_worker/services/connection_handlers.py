import asyncio
from typing import Callable

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from cloud_worker import get_logger
from cloud_worker.constants import PROJECT_RABBITMQ_QUEUE_NAME

log = get_logger(__name__)


class RabbitMQHandler:
    @staticmethod
    async def log_message(message: AbstractIncomingMessage) -> None:
        async with message.process(): # context manager - if exception, the message will be returned to the queue. also runs an ack after processing the message
            log.info(f'received message with no handler {message.body}')
            
    @staticmethod
    async def listen(queue_name :str , on_message_handler: Callable = log_message) -> None:
        connection = await aio_pika.connect(PROJECT_RABBITMQ_QUEUE_NAME)

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1) # workers can handle at most n messages at a time

            queue = await channel.declare_queue(
                queue_name, durable=True, # a durable queue is stored on disk, so data is kept even through restarts
            )

            await queue.consume(on_message_handler)

            log.info(" [*] Waiting for messages.")
            await asyncio.Future() # keep the listener running indefinitely 

    @staticmethod
    async def publish(queue_name:str, message:str) -> None:
        # Perform connection
        connection = await aio_pika.connect(PROJECT_RABBITMQ_QUEUE_NAME)

        async with connection:
            channel = await connection.channel()
            
            message_body = message.encode()

            message_obj = aio_pika.Message(
                message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            # Sending the message
            await channel.default_exchange.publish(
                message_obj, routing_key=queue_name,
            )

            log.debug(f" [x] Sent {message}")
    

