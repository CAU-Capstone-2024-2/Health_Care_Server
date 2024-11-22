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
    
    def create_form(user_id, form_id):
        with get_db() as db:
            if user := db.query(User).filter(User.uid == user_id).first():
                user.form_id = form_id
                db.commit()
                return user.form_id
    
    def remove_form(form_id):
        with get_db() as db:
            if user := db.query(User).filter(User.form_id == form_id).first():
                user.form_id = None
                db.commit()
            return True
    
    def get_form(form_id):
        with get_db() as db:
            if db.query(User).filter(User.form_id == form_id).first():
                return True
            return False
        
    def get_user_by_form_id(form_id):
        with get_db() as db:
            if user := db.query(User).filter(User.form_id == form_id).first():
                return user.uid
            return None
        
    def save_user_info(uid, age, gender, disease, subscription):
        with get_db() as db:
            if user := db.query(User).filter(User.uid == uid).first():
                user.age = age
                if gender == '남성' or gender == 'M' or gender == 'm' or gender == "male":
                    gender = 'M'
                elif gender == '여성' or gender == 'F' or gender == 'f' or gender == "female":
                    gender = 'F'
                user.gender = gender
                user.disease = disease
                user.subscription = subscription
                db.commit()
            return True
        
    def append_index(uid, index):
        with get_db() as db:
            user = db.query(User).filter(User.uid == uid).first()
            if user.used_index is None:
                user.used_index = index
            else:
                user.used_index += "," + index
            db.commit()
        return True