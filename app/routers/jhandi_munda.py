
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2, jm_util
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
# from .coins import update_coin
from typing import List

router = APIRouter(
    prefix= "/jm",
    tags=["Jhandi Munda"]
)


@router.get("/get_time_slot", response_model= schemas.JhandiMundaTiming)
def get_slot_details(db: Session = Depends(get_db)):
    slot = jm_util.get_jm_time_slot()
    if slot.is_jhandi_munda_slot_open:
        jm_util.delete_prev_slot_data(db)
    return slot



@router.post("/bid")
def bid(bid_details : schemas.JhandiMundaBidRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    
    if not jm_util.get_jm_time_slot().is_jhandi_munda_slot_open:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bidding is no longer allowed in the current slot. Please wait until the next slot.")
    
    # Delete prev slot entries
    jm_util.delete_prev_slot_data(db)

    if bid_details.bid_card_id < 1 or bid_details.bid_card_id > 6:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Invalid card id")
    
    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    if int(coin_balance.num_of_coins) < bid_details.bid_amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")

    new_entry = models.JhandiMundaBids(user_id = current_user.id, card_id = bid_details.bid_card_id, bid_amount = bid_details.bid_amount)

    db.add(new_entry)
    coin_balance.num_of_coins -= bid_details.bid_amount
    db.commit()

    return {"detail" : f"Succesfully placed bid against card number {bid_details.bid_card_id}"}



@router.get("/get_result", response_model= schemas.JhandiMundaWinnerDetailsResponseModel)
def get_result_details(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    if jm_util.get_jm_time_slot().is_jhandi_munda_slot_open:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bidding is currently in progress. Please wait until the slot is over.")
    

    user_bids_query = db.query(func.sum(models.JhandiMundaBids.bid_amount).label("bid_amount")).filter(models.JhandiMundaBids.user_id == current_user.id)

    user_bids = user_bids_query.first()

    if not user_bids or not user_bids.bid_amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You haven't participated in this slot")
    
    winning_card = jm_util.calculate_winning_card(db)



    bid_on_winning_card = db.query(func.sum(models.JhandiMundaBids.bid_amount).label("bid_amount")).filter(models.JhandiMundaBids.user_id == current_user.id, models.JhandiMundaBids.card_id == winning_card).first()

    response = schemas.JhandiMundaWinnerDetailsResponseModel(winnig_card_id = winning_card, total_bid_money = user_bids.bid_amount, is_user_winner = False)

    if not bid_on_winning_card or not bid_on_winning_card.bid_amount:
        pass
    else:
        response.is_user_winner = True
        response.bid_on_winning_card = bid_on_winning_card.bid_amount
        response.win_money = bid_on_winning_card.bid_amount * 6
        # Add coin balance
        update_coin(schemas.CoinUpdateRequest(coins=response.win_money, updation_type="add"), db, current_user)

        # Delete winning entries
        db.query(models.JhandiMundaBids).filter(models.JhandiMundaBids.user_id == current_user.id, models.JhandiMundaBids.card_id == winning_card).delete()
        db.commit()

    return response



@router.get("/get_my_bids", response_model = List[schemas.JhandiMundaMyBidsResponseModel])
def get_my_bids(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    slot = jm_util.get_jm_time_slot()

    if not slot.is_jhandi_munda_slot_open:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no active bids")

    my_bids = db.query(models.JhandiMundaBids.card_id.label("card_id"), func.sum(models.JhandiMundaBids.bid_amount).label("bid_amount")).filter(models.JhandiMundaBids.user_id == current_user.id).group_by(models.JhandiMundaBids.card_id).order_by(models.JhandiMundaBids.card_id).all()

    return my_bids