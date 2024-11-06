from Database.model import User
from Database.database import get_db
class UserService:
    def to_user_entity(uid):
        return User(uid=uid)

    def get_user(uid):
        with get_db() as db:
            return db.query(User).filter(User.uid == uid).first()
        
    def save_user(user):
        with get_db() as db:
            try:
                db.add(user)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
            
    def change_config(uid, period):
        with get_db() as db:
            user = db.query(User).filter(User.uid == uid).first()
            user.period = period
            db.commit()
        return True