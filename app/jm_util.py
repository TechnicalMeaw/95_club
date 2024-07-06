from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import time
import re
from sqlalchemy import func
import random

def get_jm_time_slot():

    now = datetime.now()

    if (now.second >= 0 and now.second < 20) or (now.second >= 30 and now.second < 50):

        current_match_end_time = datetime(now.year, now.month, now.day, now.hour, now.minute, second=19, microsecond=999999)

        if now.second >= 30:
            current_match_end_time = datetime(now.year, now.month, now.day, now.hour, now.minute, second=49, microsecond=999999)

        # Time remaining to end the match
        time_remaining = (current_match_end_time - now).total_seconds() * 1000

        return schemas.JhandiMundaTiming(is_jhandi_munda_slot_open = True, remaining_time_in_millis = time_remaining)
    
    else:
        next_slot_time = datetime(now.year, now.month, now.day, now.hour, now.minute, 30)

        if now.second >= 30:
            # next_slot_minutes = now.minute + 1
            # next_slot_hour = now.hour
            # next_slot_day = now.day

            # if next_slot_time == 60:
            #     next_slot_minutes = 0
            #     next_slot_hour += 1
            #     if next_slot_hour == 24:
            #         next_slot_hour = 0
            #         next_slot_day += 1


            next_slot_time = datetime(now.year, now.month, now.day, now.hour, now.minute, 59, 999999)

        # Time remaining for next match
        time_difference = (next_slot_time - now).total_seconds() * 1000
        
        return schemas.JhandiMundaTiming(is_jhandi_munda_slot_open = False, remaining_time_in_millis = time_difference)
    

def delete_prev_slot_data(db: Session):
    now = datetime.now()

    prev_slot_time = datetime(now.year, now.month, now.day, now.hour, now.minute, 0)

    if now.second >= 30:
        prev_slot_time = datetime(now.year, now.month, now.day, now.hour, now.minute, 29, 999999)

    db.query(models.JhandiMundaBids).filter(models.JhandiMundaBids.created_at < prev_slot_time).delete(synchronize_session=False)

    db.commit()


def calculate_winning_card(db: Session):
    winning_card_id = -1

    card_min_bid_amount = 0

    for id in range(1,7):

        card_bid_anount = db.query(func.sum(models.JhandiMundaBids.bid_amount).label("bid_amount")).filter(models.JhandiMundaBids.card_id == id).first()

        if not card_bid_anount or not card_bid_anount.bid_amount:
            card_bid_anount = 0
        else:
            card_bid_anount = card_bid_anount.bid_amount
        

        if id == 1:
            card_min_bid_amount = card_bid_anount
            winning_card_id = id
        elif card_bid_anount < card_min_bid_amount:
                card_min_bid_amount = card_bid_anount
                winning_card_id = id

    if random.randrange(0, 1000) == random.randrange(200, 300):
        return -1
    else:
        return winning_card_id

        