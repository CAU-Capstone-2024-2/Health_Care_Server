from pydantic import BaseModel

class Question(BaseModel):
    userid: str
    question: str
    