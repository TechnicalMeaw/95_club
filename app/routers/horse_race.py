
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2, horse_util
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .coins import update_coin
from typing import List

router = APIRouter(
    prefix= "/horse",
    tags=["Horse Race"]
)


@router.get("/get_slot_details", response_model=schemas.HorseMatchTiming)
def get_slot_details(db: Session = Depends(get_db)):
    slot = horse_util.get_lottery_time_left_in_millis()
    if slot.is_horse_bidding_slot_open:
        # Delete prev slot entries
        horse_util.delete_prev_slot_entries(db)
    return slot


@router.post("/bid", response_model=schemas.HTTPError)
def bid(bid_details : schemas.HorseRaceBidRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    if not horse_util.is_bidding_allowed():
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail="Bidding is no longer allowed in the current slot. Please wait until the next slot.")

    # Delete prev slot entries
    horse_util.delete_prev_slot_entries(db)

    if bid_details.bid_horse_id < 1 or bid_details.bid_horse_id > 6:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail="Invalid horse id")
    
    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    if int(coin_balance.num_of_coins) < bid_details.bid_amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    new_entry = models.HorseRaceBids(user_id = current_user.id, horse_id = bid_details.bid_horse_id, bid_amount = bid_details.bid_amount)

    db.add(new_entry)
    coin_balance.num_of_coins -= bid_details.bid_amount
    db.commit()

    return {"detail" : f"Succesfully placed bid against horse number {bid_details.bid_horse_id}"}


@router.get("/get_result_details", response_model= schemas.HorseRaceWinnerDetailsResponseModel)
def get_result_details(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    if horse_util.is_bidding_allowed():
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail="Bidding is currently in progress. Please wait until the race is finished.")

    user_bids_query = db.query(func.sum(models.HorseRaceBids.bid_amount).label("bid_amount")).filter(models.HorseRaceBids.user_id == current_user.id)

    user_bids = user_bids_query.first()

    if not user_bids or not user_bids.bid_amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You haven't participated in this slot")
    

    winning_horse_id = horse_util.calculate_winning_horse(db)
    

    bid_on_winning_horse = db.query(func.sum(models.HorseRaceBids.bid_amount).label("bid_amount")).filter(models.HorseRaceBids.user_id == current_user.id, models.HorseRaceBids.horse_id == winning_horse_id).first()

    response = schemas.HorseRaceWinnerDetailsResponseModel(winnig_horse_id = winning_horse_id, total_bid_money = user_bids.bid_amount, is_user_winner = False)

    if not bid_on_winning_horse or not bid_on_winning_horse.bid_amount:
        pass
    else:
        response.is_user_winner = True
        response.bid_on_winning_horse = bid_on_winning_horse.bid_amount
        response.win_money = bid_on_winning_horse.bid_amount * 6
        # Add coin balance
        update_coin(schemas.CoinUpdateRequest(coins=response.win_money, updation_type="add"), db, current_user)

        # Delete winning entries
        db.query(models.HorseRaceBids).filter(models.HorseRaceBids.user_id == current_user.id, models.HorseRaceBids.horse_id == winning_horse_id).delete()
        db.commit()

    return response


@router.get("/get_my_bids", response_model = List[schemas.HorseRaceMyBidsResponseModel])
def get_my_bids(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    slot = horse_util.get_lottery_time_left_in_millis()

    if not slot.is_horse_bidding_slot_open:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no active bids")

    my_bids = db.query(models.HorseRaceBids.horse_id.label("horse_id"), func.sum(models.HorseRaceBids.bid_amount).label("bid_amount")).filter(models.HorseRaceBids.user_id == current_user.id).group_by(models.HorseRaceBids.horse_id).order_by(models.HorseRaceBids.horse_id).all()

    return my_bids