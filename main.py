import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Database.database import db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.status import *
import uvicorn
from Database.database import create_database, engine
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from Router import ask
create_database()

load_dotenv("../.env")
secret = os.getenv("secret")

# 스웨거 예시 표시
SWAGGER_HEADERS = {
    "title": "SWAGGER API REFERENCE",
    "version": "1.0.0",
    "description": ""
    }




# app = FastAPI()

# 스웨거 예시 표시
app = FastAPI(
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "operationsSorter": "method",
        "filter": True,
        "tagsSorter": "alpha",
        "syntaxHighlight.theme": "tomorrow-night",
    },
    **SWAGGER_HEADERS
)

app.include_router(ask.router)


# CORS
origins = [ "*" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1500, reload=True)