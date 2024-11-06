from fastapi.responses import JSONResponse
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

router = APIRouter(prefix="/user", tags=["user"])

load_dotenv(".env")


@router.post("/config")
async def config(request: Request):
    try:
        data = await request.json()
        print(data)
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})