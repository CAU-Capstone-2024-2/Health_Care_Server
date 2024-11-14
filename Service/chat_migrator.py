from fastapi import Depends
from sqlalchemy import text
from Database.model import Chat, CompleteChat
from Database.database import get_db
from sqlalchemy.orm import Session
import re


class Migrator:
    def __init__(self):
        self.rule = re.compile(r"((qs)+(ca)+|(ca)+)|(qa)+")
        # self.rule = re.compile(r"(qs)+(ca)+")

    def migrate(self):
        sessionIds = self.get_all_session_id()
        for sessionId in sessionIds:
            chats = self.get_chat_by_session_id(sessionId)
            chat_history = "".join([str(chat.type) for chat in chats])
            print("".join([str(chat.type) for chat in chats]))
            matches = self.rule.finditer(chat_history)
            longest_match = max(matches, key=lambda match: match.end() - match.start(), default=None)
            if longest_match:
                self.migrate_chat(chats, longest_match)
            
    
    def get_all_uid(self):
        with get_db() as db:
            uids = db.execute(text("SELECT DISTINCT uid FROM chat"))
        return [uid[0] for uid in uids]
    
    def get_all_session_id(self):
        with get_db() as db:
            session_ids = db.execute(text("SELECT DISTINCT sessionId FROM chat"))
        return [session_id[0] for session_id in session_ids]
        
    def get_chat_by_uid(self, uid):
        with get_db() as db:
            return db.query(Chat).filter(Chat.uid == uid).order_by(Chat.created_at.asc(), Chat.id.asc()).all()
        
    def get_chat_by_session_id(self, sessionId):
        with get_db() as db:
            return db.query(Chat).filter(Chat.sessionId == sessionId).order_by(Chat.created_at.asc(), Chat.id.asc()).all()
    
    def migrate_chat(self, chats, longest_match):
        with get_db() as db:
            to_migrate = chats[longest_match.start():longest_match.end()]
            for chat in to_migrate:
                complete_chat = CompleteChat(chat)
                db.add(complete_chat)
                db.delete(chat)
            db.commit()