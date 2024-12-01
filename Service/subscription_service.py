import time
import requests
from Database.database import get_db
from Database.model import User
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv(".env")
BOT_ID = os.getenv("BOT_ID")
REST_API_KEY = os.getenv("REST_API_KEY")

class SubscriptionService:
    def get_subscribed_users():
        with get_db() as db:
            return db.query(User).filter(User.subscription != None, User.subscription_date != None).all()
        
    def send_subscription():
        with get_db() as db:
            users = SubscriptionService.get_subscribed_users()
            today = date.today()
            for user in users:
                if (today - user.subscription_date).days % user.subscription == 0:
                    if SubscriptionService.send_to_server(user.uid):
                        user.subscription_date = today
                        db.commit()
                    time.sleep(1)
            db.commit()
        return True
    
    def send_to_server(uid):
        json_form = {
            "event": {
                "name": "sendPersonalReport"
            },
            "user": [
                {"type": "botUserKey", "id": uid}
            ]
        }
        header = {
            "Authorization": "KakaoAK "+ REST_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post("https://bot-api.kakao.com/v2/bots/"+BOT_ID+"/talk", json=json_form, headers=header)
        if response.status_code == 200:
            return True