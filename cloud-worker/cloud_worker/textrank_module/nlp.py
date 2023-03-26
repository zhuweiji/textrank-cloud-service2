
from cloud_worker import get_logger
from gensim.parsing import preprocessing

log = get_logger(__name__)

def remove_stopwords(text):
    return preprocessing.remove_stopwords(text)