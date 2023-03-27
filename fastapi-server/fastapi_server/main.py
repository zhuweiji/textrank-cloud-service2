import asyncio
import logging

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi_server.constants import RABBITMQ_JOB_QUEUE_NAME, RABBITMQ_RESULT_QUEUE_NAME
from fastapi_server.entities.POST_bodies import Text_Transcribe_Request
from fastapi_server.entities.responses import healthcheck_response
from fastapi_server.routers import router
from fastapi_server.services.connection_handlers import RabbitMQHandler
from fastapi_server.services.task_processor import JobProcessor
from sse_starlette.sse import EventSourceResponse

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(
    title="TextRank Backend",
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router=router.router
)

tasks = set()

def run_task(coro):
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)

@app.on_event('startup')
async def before_start():
    t = run_task(
        RabbitMQHandler.listen(RABBITMQ_RESULT_QUEUE_NAME, on_message_handler=JobProcessor.handle_new_result)
    )
    tasks.add(t)

@app.get('/')
def root_endpoint():
    return healthcheck_response() 





