from pydantic import BaseModel


class Text_Transcribe_Request(BaseModel):
    text: str