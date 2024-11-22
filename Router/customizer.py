from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import requests
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
from dotenv import load_dotenv
from fastapi import Request
import os
from Service.user_service import UserService
from Service.transaction_service import TransactionService
from Data.chat import UID

router = APIRouter(prefix="/customized_info", tags=["customized_info"])

load_dotenv(".env")
BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")
BOT_ID = os.getenv("BOT_ID")
REST_API_KEY = os.getenv("REST_API_KEY")

@router.post("/request")
async def request_customized_info(request: Request):
    try:
        data = await request.json()
        uid = data['userRequest']['user']['id']
        user = UserService.get_user(uid)
        if user is None:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        age = user.age
        disease = "<disease>"+user.disease+"</disease>"
        chats = TransactionService.get_chat_by_uid_C(uid)
        chat_data = []
        for i in range(min(len(chats), 5)):
            chat_data.append(chats[i].utterance)
        string_form = f"""이 노인은 현재 {age}세이며, {disease} 질병을 앓고 있습니다. 최근 대화 내용은 다음과 같습니다:\n""" + "\n".join(chat_data)
        response = requests.post(AI_SERVER_URL + "/custom_information", json={"info": string_form})
        img_url = response.json()["img_url"]
        json_form = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleImage": {
                            "imageUrl": img_url,
                            "altText": "주기적으로 전송되는 맞춤형 건강 정보입니다."
                        }
                    }
                ]
            }
        }
        return JSONResponse(status_code=200, content=json_form)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Internal server error"})

@router.post("/test")
async def request_customized_info(request: Request, uid: UID, background_tasks: BackgroundTasks):
    json_form = {
        "event": {
            "name": "sendPersonalReport"
        },
        "user": [
            {"type": "botUserKey", "id": uid.uid}
        ]
    }
    header = {
        "Authorization": "KakaoAK "+ REST_API_KEY,
        "Content-Type": "application/json"
    }
    requests.post("https://bot-api.kakao.com/v2/bots/"+BOT_ID+"/talk", json=json_form, headers=header)