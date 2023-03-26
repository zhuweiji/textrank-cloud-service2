from typing import BinaryIO

from fastapi_server.entities.responses import endpoint_not_implemented_response


def image_rank_service(file: BinaryIO):
    return endpoint_not_implemented_response()