import math
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import String, and_, cast, delete, func, select
from typing import List, Optional
from datetime import datetime, timedelta
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
    elif result_number == 5:
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

        coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()
        if coin_balance:
            coin_balance.num_of_coins = coin_balance.num_of_coins + user_reward

        # Save in user game history
        existing_user_game_log = db.query(models.UserGameLogs).filter(models.UserGameLogs.game_id == game.id, models.UserGameLogs.user_id == current_user.id).first()
        if existing_user_game_log:
            existing_user_game_log.win_coin_value = user_reward

        # Calculate result for each bid and save in db
        all_user_bids = db.query(models.UserBids).filter(models.UserBids.user_id == current_user.id, models.UserBids.game_id == game.id).all()

        for bid in all_user_bids:
            bid.win_amount = ((bid.game_coin_price if bid.bid_number == game.result_number else 0) * 9) + \
                ((bid.game_coin_price if bid.bid_color == game.result_color else 0)  * 2) + \
                ((bid.game_coin_price if bid.bid_size == game.result_size else 0) * 2)

        db.commit()

        return {"result_number" : game.result_number,
                "result_color" : game.result_color,
                "result_size" : game.result_size,
                "total_bid": user_coin_bids_query.scalar() or 0, 
                "win_coins" : user_reward,
                "game_id": game.id}


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
    # db.commit()

    user_coin_bids_query = all_bids_coins_query.filter(models.UserBids.user_id == current_user.id)

    user_result_number_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_number == result_number).scalar() or 0
    user_result_color_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_color == result_color).scalar() or 0
    user_result_size_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_size == result_size).scalar() or 0

    user_reward = (user_result_number_bid_coins * 9) + (user_result_color_bid_coins * 2) + (user_result_size_bid_coins * 2)

    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()
    if coin_balance:
        coin_balance.num_of_coins = coin_balance.num_of_coins + user_reward

    # Save in user game history
    existing_user_game_log = db.query(models.UserGameLogs).filter(models.UserGameLogs.game_id == game.id, models.UserGameLogs.user_id == current_user.id).first()
    if existing_user_game_log:
        existing_user_game_log.win_coin_value = user_reward

    # Calculate result for each bid and save in db
    all_user_bids = db.query(models.UserBids).filter(models.UserBids.user_id == current_user.id, models.UserBids.game_id == game.id).all()

    for bid in all_user_bids:
        bid.win_amount = ((bid.game_coin_price if bid.bid_number == result_number else 0) * 9) + \
                ((bid.game_coin_price if bid.bid_color == result_color else 0)  * 2) + \
                ((bid.game_coin_price if bid.bid_size == result_size else 0) * 2)


    db.commit()

    return {"result_number" : result_number,
            "result_color" : result_color,
            "result_size" : result_size,
            "total_bid": user_coin_bids_query.scalar() or 0, 
            "win_coins" : user_reward,
            "game_id": game.id}


@router.post('/bid')
async def bid(body : schemas.GamePlayBidRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    game = db.query(models.GameLogs).filter(models.GameLogs.id == body.game_id).first()

    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid game id')
    
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

    if game_elapsed_time.total_seconds() > game_bid_time_in_seconds:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bidding is not allowed in last 10 seconds")

    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    if int(coin_balance.num_of_coins) < body.bid_amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    if body.bid_amount < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid ammount can't be less than 10")
    
    if body.bid_number:
        if body.bid_color or body.bid_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        if body.bid_number < 0 or body.bid_number > 9:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bid number")
        
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_number = body.bid_number, game_coin_price = body.bid_amount)
        db.add(new_bid)

    elif body.bid_color:
        if body.bid_number or body.bid_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_color = body.bid_color, game_coin_price = body.bid_amount)
        db.add(new_bid)

    elif body.bid_size:
        if body.bid_number or body.bid_color:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid can be either on number or color or size")
    
        new_bid = models.UserBids(user_id = current_user.id, game_id = game.id, bid_size = body.bid_size, game_coin_price = body.bid_amount)
        db.add(new_bid)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bid request")
    
    # Deduct amount
    coin_balance.num_of_coins = coin_balance.num_of_coins - body.bid_amount

    # Save in user game history
    existing_user_game_log = db.query(models.UserGameLogs).filter(models.UserGameLogs.game_id == game.id, models.UserGameLogs.user_id == current_user.id).first()

    if not existing_user_game_log:
        new_log = models.UserGameLogs(user_id = current_user.id, game_id = game.id)
        db.add(new_log)

    db.commit()
    
    return {"status": "success", "statusCode": 200, "message" : "Successfully placed bid"}


@router.get('/get_game_history', response_model=schemas.GameHistoryResponseModel)
async def get_game_history(game_type: int = 1, page: int = 1, search: Optional[str] = "", db: Session = Depends(get_db)):
    if game_type < 1 or game_type > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game type")

    game_history_query = db.query(models.GameLogs).filter(models.GameLogs.game_type == game_type, models.GameLogs.is_finished == True)\
        .filter(cast(models.GameLogs.id, String)
                .contains(search)).order_by(models.GameLogs.created_at.desc())
    
    total_count = game_history_query.count()
    total_page = math.ceil(total_count/10)
    game_history_data = game_history_query.limit(10).offset((page-1)*10).all()
    
    
    return {"status": "success", "statusCode": 200, "message" : "Successfully got game history",
            "total_count": total_count,
            "current_page": page,
            "total_page": total_page,
            "prev_page": page-1 if page > 1 else None, 
            "next_page": page+1 if page < total_page else None,
            "data" : game_history_data}


@router.get('/get_my_game_history', response_model=schemas.MyGameHistoryResponseModel)
async def get_game_history(game_type: int = 1, page: int = 1, search: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    if game_type < 1 or game_type > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game type")

    history_query = db.query(models.UserGameLogs).join(models.GameLogs).where(models.UserGameLogs.game_id == models.GameLogs.id).filter(
        models.UserGameLogs.user_id == current_user.id
        ).filter(
            models.GameLogs.game_type == game_type, models.GameLogs.is_finished == True
        ).filter(
            cast(models.GameLogs.id, String).contains(search)
            ).order_by(models.UserGameLogs.created_at.desc())
    
    total_count = history_query.count()
    total_page = math.ceil(total_count/10)
    history_data = history_query.limit(10).offset((page-1)*10).all()

    return {"status": "success", "statusCode": 200, "message" : "Successfully got my game history", 
            "total_count": total_count,
            "current_page": page,
            "total_page": total_page,
            "prev_page": page-1 if page > 1 else None, 
            "next_page": page+1 if page < total_page else None,
            "data" : history_data}



@router.get('/get_my_game_bids_history')
async def get_game_bids_history(game_type: int = 1, page: int = 1, search: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    if game_type < 1 or game_type > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game type")

    history_query = db.query(models.UserBids).join(models.GameLogs).where(models.UserBids.game_id == models.GameLogs.id).filter(
        models.UserBids.user_id == current_user.id
        ).filter(
            models.GameLogs.game_type == game_type, models.GameLogs.is_finished == True
        ).filter(
            cast(models.GameLogs.id, String).contains(search)
            ).order_by(models.UserBids.created_at.desc())
    
    total_count = history_query.count()
    total_page = math.ceil(total_count/10)
    history_data = history_query.limit(10).offset((page-1)*10).all()

    return {"status": "success", "statusCode": 200, "message" : "Successfully got my game history", 
            "total_count": total_count,
            "current_page": page,
            "total_page": total_page,
            "prev_page": page-1 if page > 1 else None, 
            "next_page": page+1 if page < total_page else None,
            "data" : history_data}



@router.get('/error_correction_and_calculate')
async def error_correction_and_calculate(db: Session = Depends(get_db)):

    # Delete game logs older than 24 hrs
    # with no bids on them
    # ----------------------------------

    # Calculate the timestamp for 24 hours ago
    time_threshold = datetime.now() - timedelta(hours=24)

    # Subquery to get all game_ids in UserBids
    subquery = select(models.UserBids.game_id).distinct()

    # Delete GameLogs where game_id is not in the subquery
    delete_query = delete(models.GameLogs).where(
        and_(
            models.GameLogs.id.not_in(subquery),
            models.GameLogs.created_at < time_threshold
        )
    )

    # Execute the delete query
    db.execute(delete_query)

    db.commit()

    all_unfinished_user_games = db.query(models.UserGameLogs).join(models.GameLogs).where(models.UserGameLogs.game_id == models.GameLogs.id)\
        .filter(models.GameLogs.is_finished == True, models.UserGameLogs.win_coin_value == None).all()
    
    for user_game_log in all_unfinished_user_games:
        # Get game log
        game = db.query(models.GameLogs).filter(models.GameLogs.id == user_game_log.game_id).first()
        if game:
            # Query to filter bids by game_id
            all_bids_coins_query = db.query(func.sum(models.UserBids.game_coin_price)).filter(models.UserBids.game_id == game.id)
        
            user_coin_bids_query = all_bids_coins_query.filter(models.UserBids.user_id == user_game_log.user_id)

            user_result_number_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_number == game.result_number).scalar() or 0
            user_result_color_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_color == game.result_color).scalar() or 0
            user_result_size_bid_coins = user_coin_bids_query.filter(models.UserBids.bid_size == game.result_size).scalar() or 0

            user_reward = (user_result_number_bid_coins * 9) + (user_result_color_bid_coins * 2) + (user_result_size_bid_coins * 2)

            coin_balance = db.query(models.Coins).filter(user_game_log.user_id == models.Coins.user_id).first()
            coin_balance.num_of_coins = coin_balance.num_of_coins + user_reward

            # Save in user game history
            user_game_log.win_coin_value = user_reward

            # Calculate result for each bid and save in db
            all_user_bids = db.query(models.UserBids).filter(models.UserBids.user_id == user_game_log.user_id, models.UserBids.game_id == game.id).all()

            for bid in all_user_bids:
                bid.win_amount = ((bid.game_coin_price if bid.bid_number == game.result_number else 0) * 9) + \
                    ((bid.game_coin_price if bid.bid_color == game.result_color else 0)  * 2) + \
                    ((bid.game_coin_price if bid.bid_size == game.result_size else 0) * 2)


            db.commit()

    return {"status": "success", "statusCode": 200, "message" : "Successfully executed"}