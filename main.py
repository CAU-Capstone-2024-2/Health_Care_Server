import sys
import os
import time
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.status import *
import schedule
from threading import Thread
import uvicorn
from Database.database import create_database, engine
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from Router import ask, user, form, customizer, read, static, tutorial
from Service.chat_migrator import Migrator
from apscheduler.schedulers.background import BackgroundScheduler
from Service.subscription_service import SubscriptionService
import pytz

create_database()

load_dotenv(".env")
secret = os.getenv("secret")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")

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
app.include_router(user.router)
app.include_router(form.router)
app.include_router(customizer.router)
app.include_router(read.router)
app.include_router(static.router)
app.include_router(tutorial.router)

from fastapi.responses import JSONResponse
from fastapi.requests import Request
# @app.exception_handler(404)
# async def not_found_handler(request: Request, exc):
#     return JSONResponse(
#         status_code=200,
#         content={"message": "You fool bro, this is not the page you are looking for"}
#     )
# CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    migrator = Migrator()

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Seoul'))
    scheduler.add_job(SubscriptionService.send_subscription, 'cron', hour=9, minute=0)
    scheduler.start()

    # 매 10분마다 get_all_uid 실행
    schedule.every(5).seconds.do(migrator.migrate)
    #schedule.every(10).minutes.do(migrator.migrate)

    # 스케줄러를 별도의 스레드에서 실행
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    uvicorn.run("main:app", host="0.0.0.0", port=1500, workers=2)
