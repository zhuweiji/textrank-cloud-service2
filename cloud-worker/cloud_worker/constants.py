import logging
import os

log = logging.getLogger(__name__)

is_dev_env = os.getenv('DEV')

RABBITMQ_RESULT_QUEUE_NAME = 'result_queue'
RABBITMQ_JOB_QUEUE_NAME    = 'job_queue'
RABBITMQ_CONNECTION_URL    = 'amqp://guest:guest@ 172.26.48.1'

if is_dev_env:
    log.info('detected dev environment')
    RABBITMQ_CONNECTION_URL    = 'amqp://guest:guest@localhost'