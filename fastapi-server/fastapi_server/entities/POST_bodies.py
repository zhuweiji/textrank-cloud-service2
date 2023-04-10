from typing import List

from pydantic import BaseModel


class Text_Transcribe_Request(BaseModel):
    text: str
    
class Sentence_Extraction_Request(BaseModel):
    text: str
    
    
class Image_Rank_with_Sentences(BaseModel):
    delimited_text: str