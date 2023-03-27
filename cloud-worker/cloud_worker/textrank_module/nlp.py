
import logging

from gensim.parsing import preprocessing

log = logging.getLogger(__name__)

def remove_stopwords(text):
    return preprocessing.remove_stopwords(text)