
import logging
import re
from typing import List

from gensim.parsing import preprocessing
from spacy.tokens import Doc, Span
from unidecode import unidecode

log = logging.getLogger(__name__)

def _decode_unicode(text:str):
    return unidecode(text)

def _remove_stopwords(text:str):
    return preprocessing.remove_stopwords(text)

def _remove_non_ascii(text:str):
    return re.sub(r"[^\x20-\x7E]+", ' ', text)

def _remove_non_core_words(docs: List[Doc]):
    included_tags = {"NOUN", "VERB", "ADJ", "ADV", "ADP", "PROPN"}
    result_sentences = []
    for doc in docs:
        result_sentences.append(
            " ".join([i.text for i in doc if i.pos_ not in included_tags])
        )
    return result_sentences
        