import base64
import hashlib
import uuid
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
# from datetime import time
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


import random
import time
# from datetime import datetime

# Global variables to store the last generated value and its timestamp
last_value = None
last_time = None

def get_random_number():
    global last_value, last_time

    # Get the current time
    now = datetime.now()

    # Define the time ranges and corresponding number ranges
    time_ranges = [
        ((8, 0), (10, 0), 850, 1050),
        ((10, 0), (12, 0), 1100, 1450),
        ((12, 0), (14, 0), 1100, 1560),
        ((14, 0), (16, 0), 1300, 1750),
        ((16, 0), (18, 0), 1400, 1800),
        ((18, 0), (22, 0), 1600, 2100),
        ((22, 0), (0, 0), 1450, 1850),
        ((0, 0), (8, 0), 1350, 2450)
    ]

    # Find the appropriate range based on the current time
    for start_time, end_time, low, high in time_ranges:
        start_hour, start_minute = start_time
        end_hour, end_minute = end_time

        if start_hour <= now.hour < end_hour or \
           (start_hour <= now.hour < 24 and end_hour == 0):
            if end_hour == 0 and now.hour == 23:
                continue
            break

    # Calculate the time difference from the last generated value
    current_time = time.time()
    if last_time is not None and (current_time - last_time) <= 10:
        return last_value

    # Generate a new random number within the specified range
    new_value = random.randint(low, high)

    # Ensure the new value does not differ by more than a random value between 3 and 40 from the last value
    if last_value is not None:
        if abs(new_value - last_value) > 60:
            difference = random.randint(3, 60)
            if new_value > last_value:
                new_value = min(last_value + difference, high)
            else:
                new_value = max(last_value - difference, low)

    # Update the last generated value and timestamp
    last_value = new_value
    last_time = current_time

    return new_value
