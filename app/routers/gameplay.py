from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .coins import update_coin
from typing import List
from datetime import datetime
import random


router = APIRouter(
    prefix= "/game",
    tags=["Game Play"]
)


def get_game_result(all_bids_coins_query) -> int:
     # Color bids
    green_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_color == models.BidColorOptions.green).scalar() or 0
    red_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_color == models.BidColorOptions.red).scalar() or 0
    violet_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_color == models.BidColorOptions.violet).scalar() or 0

    # Size bids
    big_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_size == models.BidSizeOptions.big).scalar() or 0
    small_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_size == models.BidSizeOptions.small).scalar() or 0

    # Number bids
    zero_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 0).scalar() or 0
    one_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 1).scalar() or 0
    two_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 2).scalar() or 0
    three_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 3).scalar() or 0
    four_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 4).scalar() or 0
    five_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 5).scalar() or 0
    six_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 6).scalar() or 0
    seven_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 7).scalar() or 0
    eight_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 8).scalar() or 0
    nine_bid_coins = all_bids_coins_query.filter(models.UserBids.bid_number == 9).scalar() or 0

    # Track all the possible outcomes
    possible_results = {}

    # If 0 wins
    possible_results[0] = (zero_bid_coins * 9) + (small_bid_coins * 2) + (violet_bid_coins * 2)
    # If 1 wins
    possible_results[1] = (one_bid_coins * 9) + (small_bid_coins * 2) + (green_bid_coins * 2)
    # If 2 wins
    possible_results[2] = (two_bid_coins * 9) + (small_bid_coins * 2) + (red_bid_coins * 2)
    # If 3 wins
    possible_results[3] = (three_bid_coins * 9) + (small_bid_coins * 2) + (green_bid_coins * 2)
    # If 4 wins
    possible_results[4] = (four_bid_coins * 9) + (small_bid_coins * 2) + (red_bid_coins * 2)

    # If 5 wins
    possible_results[5] = (five_bid_coins * 9) + (big_bid_coins * 2) + (violet_bid_coins * 2)
    # If 6 wins
    possible_results[6] = (six_bid_coins * 9) + (big_bid_coins * 2) + (red_bid_coins * 2)
    # If 7 wins
    possible_results[7] = (seven_bid_coins * 9) + (big_bid_coins * 2) + (green_bid_coins * 2)
    # If 8 wins
    possible_results[8] = (eight_bid_coins * 9) + (big_bid_coins * 2) + (red_bid_coins * 2)
    # If 9 wins
    possible_results[9] = (nine_bid_coins * 9) + (big_bid_coins * 2) + (green_bid_coins * 2)

    total_game_price = all_bids_coins_query.scalar() or 0

    filtered_possible_results = []
    for reslut_number, total_payable in possible_results.items():
        if total_payable <= total_game_price:
            filtered_possible_results.append(reslut_number)
    
    # Choose a rando number for fair chance
    random_result = random.choice(filtered_possible_results)
    return random_result


def get_result_color_and_size(result_number):
    if result_number == 0:
        return models.BidColorOptions.violet, models.BidSizeOptions.small
    elif result_number == 1:
        return models.BidColorOptions.violet, models.BidSizeOptions.big
    elif result_number in [1, 3]:
        return models.BidColorOptions.green, models.BidSizeOptions.small
    elif result_number in [2, 4]:
        return models.BidColorOptions.red, models.BidSizeOptions.small
    elif result_number in [6, 8]:
        return models.BidColorOptions.red, models.BidSizeOptions.big
    else:
        return models.BidColorOptions.green, models.BidSizeOptions.big
        


@router.get('/get_game_info')
async def get_game_info(game_type : int, db: Session = Depends(get_db)):
    if game_type < 1 or game_type > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game type")
    
    game_time_in_seconds = 0
    # If 30 sec game
    if game_type == 1:
        game_time_in_seconds = 30
    elif game_type == 2:
        game_time_in_seconds = 60
    elif game_type == 3:
        game_time_in_seconds = 180
    else:
        game_time_in_seconds = 300
    
    latest_game = db.query(models.GameLogs).filter(models.GameLogs.game_type == game_type).order_by(models.GameLogs.created_at.desc()).first()

    # First time playing
    if not latest_game:
        # Create a new game
        new_game = models.GameLogs(game_type = game_type)
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return {"time_remaining" : game_time_in_seconds, "game_id" : new_game.id}
    
    latest_game_naive = latest_game.created_at.replace(tzinfo=None)
    time_differnce = datetime.now() - latest_game_naive
    
    # Previous game finished
    if latest_game.is_finished:
        # Create a new game
        new_game = models.GameLogs(game_type = game_type)
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return {"time_remaining" : game_time_in_seconds, "game_id" : new_game.id}
    # Time exceeded but result not calculated
    elif time_differnce.total_seconds() >= game_time_in_seconds:
        # Calculate game result
        all_bids_coins_query = db.query(func.sum(models.UserBids.game_coin_price)).filter(models.UserBids.game_id == latest_game.id)
        result_number = get_game_result(all_bids_coins_query)
        result_color, result_size = get_result_color_and_size(result_number)

        # Store the result
        latest_game.result_number = result_number
        latest_game.result_color = result_color
        latest_game.result_size = result_size
        latest_game.is_finished = True

        # Create a new game
        new_game = models.GameLogs(game_type = game_type)
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return {"time_remaining" : game_time_in_seconds, "game_id" : new_game.id}
    else:
        return {"time_remaining" : game_time_in_seconds - time_differnce.total_seconds(), "game_id" : latest_game.id}
    

        
@router.get('/get_result')
async def get_result(game_id : int, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    game = db.query(models.GameLogs).filter(models.GameLogs.id == game_id).first()

    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid game id')
    
    # Query to filter bids by game_id
    all_bids_coins_query = db.query(func.sum(models.UserBids.game_coin_price)).filter(models.UserBids.game_id == game.id)
    
    # If already calculated result
    if game.is_finished:
        user_coin_bids_query = all_bids_coins_query.filter(models.UserBids.user_id == current_user.id)

        user_result_number_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_number == game.result_number).scalar() or 0
        user_result_color_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_color == game.result_color).scalar() or 0
        user_result_size_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_size == game.result_size).scalar() or 0

        user_reward = (user_result_number_bid_coins * 9) + (user_result_color_bid_coins * 2) + (user_result_size_bid_coins * 2)

        return {"result_number" : game.result_number,
                "result_color" : game.result_color,
                "result_size" : game.result_size,
                "total_bid": user_coin_bids_query.scalar() or 0, 
                "win_coins" : user_reward}


    # Bidding time validation
    # ------------------------
    game_bid_time_in_seconds = 0
    # If 30 sec game
    if game.game_type == 1:
        game_bid_time_in_seconds = 20
    # 1 min game
    elif game.game_type == 2:
        game_bid_time_in_seconds = 50
    # 3 min game
    elif game.game_type == 3:
        game_bid_time_in_seconds = 170
    # 5 min game
    else:
        game_bid_time_in_seconds = 290

    game_naive = game.created_at.replace(tzinfo=None)
    game_elapsed_time = datetime.now() - game_naive

    if game_elapsed_time.total_seconds() < game_bid_time_in_seconds:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't get result, bidding is going on")

    # Get result
    result_number = get_game_result(all_bids_coins_query)
   
    result_color, result_size = get_result_color_and_size(result_number)

    # Store the result
    game.result_number = result_number
    game.result_color = result_color
    game.result_size = result_size
    game.is_finished = True
    db.commit()

    user_coin_bids_query = all_bids_coins_query.filter(models.UserBids.user_id == current_user.id)

    user_result_number_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_number == result_number).scalar() or 0
    user_result_color_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_color == result_color).scalar() or 0
    user_result_size_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_size == result_size).scalar() or 0

    user_reward = (user_result_number_bid_coins * 9) + (user_result_color_bid_coins * 2) + (user_result_size_bid_coins * 2)

    return {"result_number" : result_number,
            "result_color" : result_color,
            "result_size" : result_size,
            "total_bid": user_coin_bids_query.scalar() or 0, 
            "win_coins" : user_reward}


@router.post('/bid')
async def bid(body : schemas.GamePlayBidRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    game = db.query(models.GameLogs).filter(models.GameLogs.id == body.game_id).first()

    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid game id')
    
    # if not body.bid_number and not body.bid_color and not body.bid_size:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bid request")
    
    if body.bid_amount < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid ammount can't be less than 10")
    
    if body.bid_number:
        if body.bid_color or body.bid_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        if body.bid_number < 0 or body.bid_number > 9:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bid number")
        
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_number = body.bid_number, game_coin_price = body.bid_amount)
        db.add(new_bid)
        db.commit()

    elif body.bid_color:
        if body.bid_number or body.bid_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_color = body.bid_color, game_coin_price = body.bid_amount)
        db.add(new_bid)
        db.commit()

    elif body.bid_size:
        if body.bid_number or body.bid_color:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_size = body.bid_size, game_coin_price = body.bid_amount)
        db.add(new_bid)
        db.commit()

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bid request")
    
    return {"detail": "Successfully placed bid"}
    