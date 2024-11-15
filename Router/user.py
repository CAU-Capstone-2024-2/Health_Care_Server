from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
from dotenv import load_dotenv
from fastapi import Request


from Service.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])

load_dotenv(".env")

@router.post("/config")
async def config(request: Request):
    try:
        data = await request.json()
        uid = data['userRequest']['user']['id']
        subscription = data['action']['clientExtra']['subscription']
        user = UserService.get_user(uid)
        if not (user.age or user.gender):
            json_form = {
                "version": "2.0",
                "template": {
                    "outputs": [
                    {
                        "textCard": {
                        "title": "맞춤형 정보 제공 동의를 하지 않았어요",
                        "description": "맞춤형 정보 제공 동의를 하지 않아서 맞춤형 정보 제공 주기를 설정할 수 없어요.\n아래의 시작하기를 눌러서 맞춤형 정보 제공 동의를 해주세요.",
                        "buttons": [
                            {
                            "action": "message",
                            "label": "시작하기",
                            "messageText": "시작하기"
                            },
                            {
                            "action": "message",
                            "label": "맞춤형 정보 수신 주기란?",
                            "messageText": "맞춤형 정보 수신 주기란?"
                            }
                        ]
                        }
                    }
                    ]
                }
            }
            return JSONResponse(status_code=200, content=json_form)
        UserService.change_config(uid, subscription)
        json_form = {
            "version": "2.0",
            "template": {
                "outputs": [
                {
                    "textCard": {
                    "title": "맞춤형 정보 주기 설정 완료!",
                    "description": "맞춤형 정보 주기가 "+subscription+"일로 설정되었어요"
                    }
                }
                ]
            }
        }
        return JSONResponse(status_code=HTTP_200_OK, content=json_form)
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
