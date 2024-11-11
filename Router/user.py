from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
import os
from dotenv import load_dotenv
from fastapi import Request
import requests
from Service.transaction_service import TransactionService
from sqlalchemy.orm import Session
import ast
import uuid


from Service.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])

load_dotenv(".env")


@router.post("/config")
async def config(request: Request):
    try:
        data = await request.json()
        uid = data['userRequest']['user']['id']
        period = data['action']['clientExtra']['period']
        UserService.change_config(uid, period)
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
