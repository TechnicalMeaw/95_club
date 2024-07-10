import base64
import hashlib
import uuid
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from datetime import time
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(password : str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_lottery_time_left_in_millis():
    now = datetime.now()
    nine_pm = datetime(now.year, now.month, now.day, 14, 55, 0)  # Set the time to 8:55 PM

    twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)   # Set the time to 12:00 AM

    if (twelve_am - now).total_seconds() < 0:
        nine_pm = datetime(now.year, now.month, now.day + 1, 14, 55, 0)

    # Calculate the time difference in milliseconds
    time_difference = (nine_pm - now).total_seconds() * 1000
    return int(time_difference)



def is_lottery_active(timeZoneOffset):

    now = datetime.now()
    nine_pm = datetime(now.year, now.month, now.day-1, 18, 0, 0)  # Set the time to 12 AM

    # twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)




    # Calculate the time difference in milliseconds
    time_difference = (nine_pm - now).total_seconds() * 1000

    return get_lottery_time_left_in_millis() > 0 and int(time_difference) < 0
    



def delete_prev_lottery_data(db: Session, timeZoneOffset):
    now = datetime.now()

    # totalSeconds = timeZoneOffset // 1000
    # totalMin = totalSeconds // 60

    # totalHrsToDeduct = totalMin // 60
    # totalMinToDeduct = totalMin % 60
    # totalSecondsToDeduct = totalSeconds % 60

    # actualMin = 0
    # actualSec = 0

    # if totalSecondsToDeduct > 0:
    #     totalMinToDeduct += 1
    #     actualSec = 60 - totalSecondsToDeduct

    # if totalMinToDeduct > 0:
    #     totalHrsToDeduct += 1
    #     actualMin = 60 - totalMinToDeduct

    
    # db.query(models.Lottery).filter(models.Lottery.created_at < datetime(now.year, now.month, now.day, 10 - totalHrsToDeduct, actualMin, actualSec)).delete(synchronize_session=False)

    twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)   # Set the time to 12:00 AM

    if (twelve_am - now).total_seconds() > 0:
        twelve_am = datetime(now.year, now.month, now.day - 1 , 18, 0, 0)



    db.query(models.Lottery).filter(models.Lottery.created_at < twelve_am).delete(synchronize_session=False)

    db.commit()


def delete_prev_winner(db: Session):
    now = datetime.now()

    twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)   # Set the time to 12:00 AM

    if (twelve_am - now).total_seconds() > 0:
        twelve_am = datetime(now.year, now.month, now.day - 1 , 18, 0, 0)

    db.query(models.LotteryWinners).filter(models.LotteryWinners.created_at < twelve_am).delete(synchronize_session=False)

    db.commit() 


def split_phone_number(phone_number):
    pattern = r'^(\+\d{1,3})(\d{10})$'
    match = re.match(pattern, phone_number)
    if match:
        country_code = match.group(1)
        number = match.group(2)
        return country_code, number
    else:
        return None, None
    
def is_email(email):
    pattern = r'^\S+@\S+\.\S+$'
    return re.match(pattern, email) is not None

def is_phone_number(phone_number):
    pattern = r'^\+?[0-9]+(?:\s*-?\s*[0-9]+)*$'
    return re.match(pattern, phone_number) is not None


def generate_unique_referral_code(unique_attribute: str):
    # Generate a UUID
    uuid_str = str(uuid.uuid4())
    
    # Combine UUID with a unique attribute of the user
    combined_str = uuid_str + unique_attribute
    
    # Hash the combination using SHA-256
    hash_object = hashlib.sha256(combined_str.encode())
    
    # Encode the hash in base64
    base64_str = base64.urlsafe_b64encode(hash_object.digest()).decode('utf-8').rstrip('=')
    
    # Truncate to 8 characters
    referral_code = base64_str[:8]
    
    return referral_code[0:7:] + referral_code[7::].replace('-', '0')
