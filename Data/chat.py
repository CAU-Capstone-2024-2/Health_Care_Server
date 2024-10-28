from pydantic import BaseModel

class QuestionData(BaseModel):
    uid: str
    utterance: str
    sessionId: str
    
class QuestionDataServer(BaseModel):
    uid: str
    utterance: str
    created_at: str

class AnswerData(BaseModel):
    sessionId: str
    answer: str

class AnswerDataServer(BaseModel):
    uid: str
    answer: str
    created_at: str