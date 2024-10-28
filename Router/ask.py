from fastapi.responses import JSONResponse
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter
from starlette.status import *
import os
from Data.question import Question
from dotenv import load_dotenv
from fastapi import Request
import requests


router = APIRouter(tags=["ask"], prefix="/api")
load_dotenv("../.env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
@router.post("/ask")
async def ask(request: Request, question: Question):
    try:
        db = get_db()
        # 대화 저장 코드
        response = requests.post(AI_SERVER_URL+"/ask", json={"question": question.utterance})
        response_text = response.json()
        print(response_text.get("answer"))
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
@router.post("/answer")
async def answer(request: Request, question: Question):
    try:
        db = get_db()
        # 대화 저장 코드
        response = requests.post(AI_SERVER_URL+"/answer", json={"question": question.utterance})
        response_text = response.json()
        print(response_text.get("answer"))
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})