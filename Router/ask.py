from fastapi.responses import JSONResponse
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter
from starlette.status import *
import os
from dotenv import load_dotenv
from fastapi import Request

router = APIRouter(tags=["ask"], prefix="/api")

@router.post("/ask")
async def ask(request: Request):
    try:
        db = get_db()
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})