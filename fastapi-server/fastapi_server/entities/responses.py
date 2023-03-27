from dataclasses import dataclass

from fastapi import Response


def job_created_response(task_id:str):
    return {'job_created': task_id}

def text_response(text:str):
    return {'message': text}

def healthcheck_response():
    return {'message': "we're up!"}

def endpoint_not_implemented_response():
    return {'message': 'this endpoint has not been completed'}