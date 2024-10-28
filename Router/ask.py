from fastapi.responses import JSONResponse
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends
from starlette.status import *
import os
from Data.chat import QuestionData, AnswerData
from dotenv import load_dotenv
from fastapi import Request
import requests
from Service.transaction_service import TransactionService


router = APIRouter(tags=["ask"], prefix="/api")
load_dotenv("../.env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")

@router.post("/ask")
async def ask(request: Request, question: QuestionData, db: requests.Session = Depends(get_db)):
    try:
        # 대화 저장 코드
        response = requests.post(AI_SERVER_URL+"/ask", json={"question": question.utterance})
        TransactionService.save_chat(db, TransactionService.to_question_entity(question))
        response_text = response.json()
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@router.post("/answer")
async def answer(request: Request, answer: AnswerData, db: requests.Session = Depends(get_db)):
    try:
        TransactionService.save_chat(db, TransactionService.to_answer_entity(answer))
        requests.post(FRONTEND_SERVER_URL+"/answer", json={"answer": answer.answer})
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@router.get("/test")
async def test(db: requests.Session = Depends(get_db)):
    temp = TransactionService.get_chat_by_uid(db, "test")
    print([(i.utterance, i.created_at) for i in temp])
    return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})