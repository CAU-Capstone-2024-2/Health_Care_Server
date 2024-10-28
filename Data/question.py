from pydantic import BaseModel

class Question(BaseModel):
    uid: str
    utterance: str
    sessionId: str
    