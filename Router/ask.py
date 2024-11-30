import json
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
from ahocorasick import Automaton
from Service.aes_service import AesService


router = APIRouter(prefix="/api")
load_dotenv(".env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")
with open('Resources/word_dictionary.json', 'r', encoding='utf-8') as file:
    word_list = json.load(file)

# Aho-Corasick 트라이 생성
automaton = Automaton()

# 단어와 정의를 트라이에 추가
for entry in word_list:
    word, definition = entry.split(": ", 1)
    automaton.add_word(word, (word, definition))

# 트라이를 완료 상태로 만듭니다.
automaton.make_automaton()

@router.post("/ask", tags=["ask"])
async def ask(request: Request, question: QuestionData, background_tasks: BackgroundTasks):
    try:
        # 대화 저장 코드
        if UserService.get_user(question.uid) is None:
            UserService.save_user(UserService.to_user_entity(question.uid))
        user = UserService.get_user(question.uid)
        question.info = ""
        if user.age:
            question.info += f"""이 노인은 현재 {user.age}세입니다."""
        if user.disease:
            question.info += f"""이 노인은 {user.disease}에 관심을 가지고 있습니다."""
        print(question.model_dump())
        if question.is_from_list:
            TransactionService.save_chat(TransactionService.to_question_entity_c(question)) 
            background_tasks.add_task(send_choice_to_ai_server, question)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        TransactionService.save_chat(TransactionService.to_question_entity(question))
        background_tasks.add_task(send_request_to_ai_server, question)
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
def send_request_to_ai_server(question: QuestionData):
    response = requests.post(AI_SERVER_URL + "/qsmaker", json=question.model_dump())

def send_choice_to_ai_server(question: QuestionData):
    response = requests.post(AI_SERVER_URL + "/ask", json=question.model_dump())
    
@router.post("/answer", tags=["answer"])
async def answer(request: Request, answer: AnswerData, background_tasks: BackgroundTasks):
    try:
        TransactionService.save_chat(TransactionService.to_answer_entity(answer))
        if answer.status_code == 211:
            print(answer.clarifying_questions)
            question = TransactionService.get_chat_by_sessionId_Q(answer.sessionId)
            data = QuestionData(uid=answer.uid, question=str(answer.clarifying_questions), sessionId=answer.sessionId)
            data.originalQuestion = question.utterance
            background_tasks.add_task(send_choice_to_frontend_server, data)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        elif answer.status_code == 212:
            print(answer.clarifying_questions)
            question = TransactionService.get_chat_by_sessionId_Q(answer.sessionId)
            data = QuestionData(uid=answer.uid, question=str(answer.clarifying_questions), sessionId=answer.sessionId)
            data.isAcute = True
            background_tasks.add_task(send_choice_to_frontend_server, data)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        elif answer.status_code == 423:
            print(answer.answer)
            TransactionService.delete_chat_by_sessionId(answer.sessionId)
            background_tasks.add_task(send_simple_text_to_frontend_server, answer)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        elif answer.status_code == 201:
            print(answer.answer)
            TransactionService.delete_chat_by_sessionId(answer.sessionId)
            background_tasks.add_task(send_simple_text_to_frontend_server, answer)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        elif answer.status_code == 202:
            print(answer.answer)
            answer.answer = json.loads(answer.answer)
            answer.answer["content"]["definitions"] = extract_definitions(answer.answer['content']['answer'])
            answer.answer["tts_key"]= AesService.encrypt(answer.answer)
            answer.answer = json.dumps(answer.answer)
            background_tasks.add_task(send_poster_to_frontend_server, answer)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        elif answer.status_code == 203:
            print(answer.answer)
            background_tasks.add_task(send_acute_to_frontend_server, answer)
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
def extract_definitions(answer: str) -> list:
    definitions = []
    seen_words = set()  # 이미 찾은 단어를 추적하기 위한 집합
    for end_index, (word, definition) in automaton.iter(answer):
        if word not in seen_words:  # 단어가 이미 처리된 적이 없는 경우에만 추가
            definitions.append({"word": word, "definition": definition})
            seen_words.add(word)  # 단어를 집합에 추가하여 중복 방지 
    return definitions

def send_choice_to_frontend_server(question: QuestionData):
    requests.post(FRONTEND_SERVER_URL + "/kakao/callback-response/list-card", json=question.model_dump())

def send_poster_to_frontend_server(answer: AnswerData):
    requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/poster", json=answer.model_dump())

def send_simple_text_to_frontend_server(answer: AnswerData):
    requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/simple-text", json=answer.model_dump())

def send_acute_to_frontend_server(answer: AnswerData):
    requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/acute", json=answer.model_dump())