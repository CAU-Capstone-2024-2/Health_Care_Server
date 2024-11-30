from pydantic import BaseModel

class TTSData(BaseModel):
    key: str
    string: str