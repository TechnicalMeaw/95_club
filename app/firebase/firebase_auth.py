import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

__cred = credentials.Certificate("./venv/serviceAccountKey.json")
firebase_admin.initialize_app(__cred)



def get_firebase_user(uid : str):
    try:
        user = auth.get_user(uid)        
        return user.__dict__
    except Exception:
        return None

def get_firebase_user_from_email(email: str):
    try:
        user = auth.get_user_by_email(email)        
        return user.__dict__
    except Exception:
        return None
    
def get_firebase_user_from_phone(phone: str):
    try:
        user = auth.get_user_by_phone_number(phone)        
        return user.__dict__
    except Exception:
        return None

def delete_account(uid: str):
    try:
        auth.delete_user(uid)
        return True
    except Exception:
        return False
    