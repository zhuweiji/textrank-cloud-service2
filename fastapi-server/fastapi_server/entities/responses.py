from dataclasses import dataclass


def text_response(text:str):
    return {'message': text}

def healthcheck_response():
    return {'message': "we're up!"}

def endpoint_not_implemented_response():
    return {'message': 'this endpoint has not been completed'}