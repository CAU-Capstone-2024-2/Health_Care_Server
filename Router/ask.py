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
from Service.user_service import UserService
from sqlalchemy.orm import Session
import ast


router = APIRouter(prefix="/api")
load_dotenv(".env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")

@router.post("/ask", tags=["ask"])
async def ask(request: Request, question: QuestionData, background_tasks: BackgroundTasks):
    try:
        # 대화 저장 코드
        if UserService.get_user(question.uid) is None:
            UserService.save_user(UserService.to_user_entity(question.uid))
        last_chat = TransactionService.find_last_chat_by_uid(question.uid)
        # if question.is_from_list:
        if last_chat is not None and question.question in last_chat.utterance:
            last_chat = TransactionService.find_last_chat_by_uid(question.uid)
            if last_chat is None:
                TransactionService.save_chat(TransactionService.to_question_entity_c(question))
            elif last_chat.type == 's' and question.question in last_chat.utterance:
                # 채팅을 C로 저장하고 AI한테 넘기기
                TransactionService.save_chat(TransactionService.to_question_entity_c(question))
            else:
                # 이건 리스트에 있었지만 현재 대화에는 없는 경우
                pass
            background_tasks.add_task(send_choice_to_ai_server, question)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        TransactionService.save_chat(TransactionService.to_question_entity(question))
        print(question.model_dump())
        background_tasks.add_task(send_request_to_ai_server, question)
        # response_text = response.json()
        # TransactionService.save_chat(db, TransactionService.to_answer_entity(AnswerData(sessionId=question.sessionId, uid=question.uid, answer=response_text["answer"])))
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
def send_request_to_ai_server(question: QuestionData):
    response = requests.post(AI_SERVER_URL + "/qsmaker", json=question.model_dump())
    print(response.json())

def send_choice_to_ai_server(question: QuestionData):
    response = requests.post(AI_SERVER_URL + "/ask", json=question.model_dump())
    print(response.json())
    
@router.post("/answer", tags=["answer"])
async def answer(request: Request, answer: AnswerData, background_tasks: BackgroundTasks):
    try:
        TransactionService.save_chat(TransactionService.to_answer_entity(answer))
        if answer.clarifying_questions is not None:
            print(answer.clarifying_questions)
            background_tasks.add_task(send_choice_to_frontend_server, QuestionData(uid=answer.uid, question=str(answer.clarifying_questions), sessionId=answer.sessionId))
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        print(answer.answer)
        background_tasks.add_task(send_answer_to_frontend_server, answer)
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})

def send_choice_to_frontend_server(question: QuestionData):
    requests.post(FRONTEND_SERVER_URL + "/kakao/callback-response/list-card", json=question.model_dump())

def send_answer_to_frontend_server(answer: AnswerData):
    requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/poster", json=answer.model_dump())

@router.get("/test")
async def test():
    temp = TransactionService.get_chat_by_uid("test")
    print([(i.utterance, i.created_at) for i in temp])
    return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})