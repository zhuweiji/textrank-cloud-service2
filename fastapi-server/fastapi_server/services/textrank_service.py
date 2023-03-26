from fastapi_server import get_logger
from fastapi_server.entities.responses import endpoint_not_implemented_response

log = get_logger(__name__)


def text_rank_service(request_text: str):
    return endpoint_not_implemented_response()
    log.debug("Message to be analyzed : {}".format(request_text))
    result = keyword_extraction__undirected(request_text)
    
    result_as_str = [str(i) for i in result]
    result_as_str = ", ".join(result_as_str)
    
    log.debug("Extracted Keywords = {}".format(result))
    return text_response(result_as_str)
