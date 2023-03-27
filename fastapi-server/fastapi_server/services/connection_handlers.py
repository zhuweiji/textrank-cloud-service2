import asyncio
import inspect
import logging
import tempfile
from typing import BinaryIO, Callable, Coroutine, Union

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from fastapi_server.constants import RABBITMQ_CONNECTION_URL, RABBITMQ_JOB_QUEUE_NAME

log = logging.getLogger(__name__)


class RabbitMQHandler:
    @classmethod
    async def listen(cls, queue_name:str , on_message_handler: Union[Callable, Coroutine]=None) -> None:
        connection = await aio_pika.connect(RABBITMQ_CONNECTION_URL)

        if on_message_handler:
            on_message_handler = cls.wrap_message_handler(on_message_handler)
        else:
            log_messages = lambda x: log.warning(f"Unhandled in queue: {queue_name} message on : {x.headers}")
            on_message_handler = cls.wrap_message_handler(log_messages)

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1) # workers can handle at most n messages at a time

            queue = await channel.declare_queue(
                queue_name, durable=True, # a durable queue is stored on disk, so data is kept even through restarts
            )
            
            # log.info(on_message_handler)
            await queue.consume(on_message_handler)

            log.info(f" [*] Waiting for messages in queue {queue_name}")
            await asyncio.Future() # keep the listener running indefinitely 

    @classmethod
    async def publish(cls, queue_name:str, message: Union[str, BinaryIO], headers=None) -> None:
        headers = headers or {}
        connection = await aio_pika.connect(RABBITMQ_CONNECTION_URL)

        async with connection:
            channel = await connection.channel()
            
            if isinstance(message, str):
                message_body = message.encode()
            elif isinstance(message, (BinaryIO, tempfile.SpooledTemporaryFile)):
                message_body = message.read()
            else:
                log.exception(f"Tried to publish message of type{type(message)}")
                raise ValueError

            message_obj = aio_pika.Message(
                message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers=headers
            )

            # Sending the message
            await channel.default_exchange.publish(
                message_obj, routing_key=queue_name,
            )
        log.debug(f'sent on channel {queue_name} | {message_obj}')

    @classmethod
    def wrap_message_handler(cls, f: Union[Callable, Coroutine]):
        if inspect.iscoroutinefunction(f):
            return cls._wrap_asynchronous_message_handler(f)
        elif isinstance(f, Callable):
            return cls._wrap_synchronous_message_handler(f)
        else:
            raise ValueError
            
    @staticmethod
    def _wrap_synchronous_message_handler(f: Callable):
        async def wrapper(message):
            async with message.process(): # context manager - if exception, the message will be returned to the queue. also runs an ack after processing the message
                f(message)
        return wrapper
    
    @staticmethod
    def _wrap_asynchronous_message_handler(coro: Coroutine):
        async def wrapper(message):
            async with message.process(): # context manager - if exception, the message will be returned to the queue. also runs an ack after processing the message
                await coro(message)
        return wrapper

