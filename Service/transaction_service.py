from datetime import datetime, timezone, timedelta
from Database.model import Chat
from Data.chat import QuestionData, AnswerData
class TransactionService:

    #sess
    def to_question_entity(question:QuestionData):
        return Chat(utterance=question.utterance, uid = question.uid, isuser=True)
    
    def to_answer_entity(answer:AnswerData):
        return Chat(utterance=answer.answer, uid = answer.uid, isuser=False)
    
    # def to_question_data(question:Chat):
    #     return QuestionData(uid=question.uid, utterance=question.utterance, created_at=question.created_at)
    
    def save_chat(db, question:Chat):
        try:
            db.add(question)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_chat_by_uid(db, uid:str):
        try:
            return db.query(Chat).filter(Chat.uid == uid).order_by(Chat.created_at.desc()).all()
        except Exception as e:
            raise e
        finally:
            db.close()