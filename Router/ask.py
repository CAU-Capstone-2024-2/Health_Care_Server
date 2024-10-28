from fastapi.responses import JSONResponse
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
import os
from Data.chat import QuestionData, AnswerData
from dotenv import load_dotenv
from fastapi import Request
import requests
from Service.transaction_service import TransactionService
from sqlalchemy.orm import Session
import ast


router = APIRouter(prefix="/api")
load_dotenv(".env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")

@router.post("/ask", tags=["ask"])
async def ask(request: Request, question: QuestionData, db: Session = Depends(get_db)):
    try:
        # 대화 저장 코드
        TransactionService.save_chat(db, TransactionService.to_question_entity(question))
        print(question.model_dump())
        response = requests.post(AI_SERVER_URL+"/qsmaker", json=question.model_dump())
        print(response.json())
        # response_text = response.json()
        # TransactionService.save_chat(db, TransactionService.to_answer_entity(AnswerData(sessionId=question.sessionId, uid=question.uid, answer=response_text["answer"])))
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@router.post("/answer", tags=["answer"])
async def answer(request: Request, answer: AnswerData, db: Session = Depends(get_db)):
    try:
        TransactionService.save_chat(db, TransactionService.to_answer_entity(answer))
        if answer.clarifying_questions is not None:
            print(answer.clarifying_questions)
            entity = TransactionService.to_answer_entity(answer)
            entity.isuser = True
            entity.utterance = str(ast.literal_eval(entity.utterance)[0])
            TransactionService.save_chat(db, entity)
            response = requests.post(AI_SERVER_URL+"/ask", json=QuestionData(uid=answer.uid, question=answer.clarifying_questions[0], sessionId=answer.sessionId).model_dump())
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        print(answer.answer)
        requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/poster", json=answer.model_dump())
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})

@router.get("/test")
async def test(db: requests.Session = Depends(get_db)):
    temp = TransactionService.get_chat_by_uid(db, "test")
    print([(i.utterance, i.created_at) for i in temp])
    return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})