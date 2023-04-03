from dataclasses import dataclass
from typing import List

from fastapi import Response


def job_created_response__multiple(task_ids:List[str]):
    return {'task_id_list': task_ids}

def job_created_response(task_id:str):
    return {'task_id': task_id}

def job_completed_response(task_id:str, result):
    return {
        'task_id': task_id,
        'result': result
    }

def text_response(text:str):
    return {'message': text}

def list_response(l: List):
    return {'data': l}

def healthcheck_response():
    return {'message': "we're up!"}

def endpoint_not_implemented_response():
    return {'message': 'this endpoint has not been completed'}