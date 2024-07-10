from typing import Optional, List
from fastapi import status, HTTPException, Depends, APIRouter

# from app.routers.coins import update_coin
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import cast
from sqlalchemy import String
from datetime import datetime

router = APIRouter(
    prefix= "/lottery",
    tags=["Lottery"]
)

@router.post("/buy", response_model=List[schemas.LotteryOutResponse])
def buy_lottery(lotteryBuyData : schemas.BuyLotteryRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    
    # if lotteryBuyData.timeZoneOffsetFromUtc != None:
    #     if not utils.is_lottery_active(lotteryBuyData.timeZoneOffsetFromUtc):
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lottery buying time is over")
    #     utils.delete_prev_lottery_data(db, lotteryBuyData.timeZoneOffsetFromUtc)
    # else:

    if not utils.is_lottery_active(0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lottery buying time is over")
    
    utils.delete_prev_lottery_data(db, 0)
    

    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")
    
    if int(coin_balance.num_of_coins) < lotteryBuyData.amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance is not enough")

    num_of_tickets = lotteryBuyData.amount//20

    for _ in range(num_of_tickets):
        lottery_entry = models.Lottery(user_id = current_user.id, lottery_coin_price = 20)
    
        db.add(lottery_entry)
        coin_balance.num_of_coins -= 20
    
    db.commit()

    user_entries = db.query(models.Lottery).filter(models.Lottery.user_id == current_user.id).all()

    return user_entries


# Get All Entries

@router.get("/participants", response_model=List[schemas.LotteryOutResponse])
def get_all_participants(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user), 
                         pageNo : int = 1, search: Optional[str] = ""):
    
    now = datetime.now()
    twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)   # Set the time to 12:00 AM

    if (twelve_am - now).total_seconds() > 0:
        twelve_am = datetime(now.year, now.month, now.day - 1 , 18, 0, 0)
    
    user_entries = db.query(models.Lottery).filter(models.Lottery.created_at > twelve_am).filter(cast(models.Lottery.lottery_token, String).contains(search)).order_by(models.Lottery.lottery_token).limit(10).offset((pageNo-1)*10).all()

    if not user_entries or len(user_entries) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entries not found")

    return user_entries



# Get My Tickets

@router.get("/get_all_my_entries", response_model=List[schemas.LotteryOutResponse])
def get_my_entries(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user), search: Optional[str] = ""):

    now = datetime.now()

    twelve_am = datetime(now.year, now.month, now.day, 18, 0, 0)   # Set the time to 12:00 AM

    if (twelve_am - now).total_seconds() > 0:
        twelve_am = datetime(now.year, now.month, now.day - 1 , 18, 0, 0)

    
    user_entries = db.query(models.Lottery).filter(models.Lottery.user_id == current_user.id).filter(models.Lottery.created_at > twelve_am).filter(cast(models.Lottery.lottery_token, String).contains(search)).order_by(0 - models.Lottery.lottery_token).all()

    if not user_entries or len(user_entries) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No entries found")

    return user_entries



@router.get("/get_time_left_in_millis", response_model= schemas.TimeLeftResponse)
def get_time_left_in_millis(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    return {"time_left_in_millis" : utils.get_lottery_time_left_in_millis()}



# ############################################################ #
# 
# Winner List

@router.get("/get_all_winners", response_model=List[schemas.LotteryWinner])
def get_all_winners(db: Session = Depends(get_db)):
    all_winners = db.query(models.LotteryWinners).order_by(0 - models.LotteryWinners.position).all()

    if utils.get_lottery_time_left_in_millis() + 300000 < 0: # if lottery ended (9PM)
    # if True:
        for winner in all_winners:
            if not winner.is_amount_credited:
                # Get winning prize
                prize_money = db.query(models.LotteryPrize).filter(winner.position == models.LotteryPrize.rank_no).first()
                # Add coin balance
                winning_user = db.query(models.User).filter(models.User.id == winner.user_id).first()
                update_coin(schemas.CoinUpdateRequest(coins=prize_money.prize_money, updation_type="add"), db, winning_user)
                winner.is_amount_credited = True
    db.commit()
    return all_winners


@router.post("/set_lottery_winner", response_model=List[schemas.LotteryWinner])
def set_winner(winnerData : schemas.SetLotteryWinnerRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    utils.delete_prev_winner(db)

    prev_winner_rank = db.query(models.LotteryWinners).filter(models.LotteryWinners.position == winnerData.rank).first()

    if prev_winner_rank:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This rank is already in the winners list")
    
    lottery_participate = db.query(models.Lottery).filter(models.Lottery.lottery_token == winnerData.token).first()

    if not lottery_participate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lottery number does not exist")

    
    # prev_winner_entry = db.query(models.LotteryWinners).filter(models.LotteryWinners.user_id == lottery_participate.user_id).first()

    # if prev_winner_entry:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user is already in the winners list")

    newWinner = models.LotteryWinners(lottery_token_no = winnerData.token, user_id = lottery_participate.user_id, position = winnerData.rank)
    db.add(newWinner)

    lottery_participate.is_winner = True

    db.commit()

    all_winners = db.query(models.LotteryWinners).all()
    return all_winners


@router.post("/remove_lottery_winner", response_model=List[schemas.LotteryWinner])
def remove_winner(winnerData : schemas.RemoveLotteryWinnerRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_winner_entry = db.query(models.LotteryWinners).filter(models.LotteryWinners.lottery_token_no == winnerData.token).first()

    if not prev_winner_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Winner not found")
    
    lottery_participate = db.query(models.Lottery).filter(models.Lottery.lottery_token == winnerData.token).first()

    lottery_participate.is_winner = False
    
    db.delete(prev_winner_entry)
    db.commit()

    all_winners = db.query(models.LotteryWinners).all()
    return all_winners
    
@router.post("/modify_lottery_winner", response_model=List[schemas.LotteryWinner])
def modify_lottery_winner(winnerData : schemas.SetLotteryWinnerRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_winner_entry = db.query(models.LotteryWinners).filter(models.LotteryWinners.lottery_token_no == winnerData.token).first()
    if not prev_winner_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Winner not found")
    
    prev_winner_entry.position = winnerData.rank

    db.commit()

    all_winners = db.query(models.LotteryWinners).all()
    return all_winners

# ############################################################ #
# 
# 


# Prize Pool
@router.get("/get_lottery_prizepool", response_model=List[schemas.LotteryPrize])
def get_lottery_prizepool(db: Session = Depends(get_db)):
    allPrize = db.query(models.LotteryPrize).order_by(models.LotteryPrize.rank_no).all()

    return allPrize

@router.post("/add_lottery_prize_pool", response_model=List[schemas.LotteryPrize])
def add_lottery_prize_pool(prizeData: schemas.LotteryPrize, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_entry = db.query(models.LotteryPrize).filter(models.LotteryPrize.rank_no == prizeData.rank_no).first()

    if prev_entry:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rank is already present")
    
    new_entry = models.LotteryPrize(rank_no = prizeData.rank_no, prize_money = prizeData.prize_money)

    db.add(new_entry)
    db.commit()

    allPrize = db.query(models.LotteryPrize).all()
    return allPrize


@router.post("/modify_lottery_prize_pool", response_model=List[schemas.LotteryPrize])
def modify_lottery_prize_pool(prizeData: schemas.LotteryPrize, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_entry = db.query(models.LotteryPrize).filter(models.LotteryPrize.rank_no == prizeData.rank_no).first()

    if not prev_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rank does not exist")
    
    prev_entry.rank_no = prizeData.rank_no
    prev_entry.prize_money = prizeData.prize_money

    db.commit()

    allPrize = db.query(models.LotteryPrize).all()
    return allPrize


@router.post("/delete_lottery_prizepool", response_model=List[schemas.LotteryPrize])
def delete_lottery_prizepool(prizeData : schemas.LotteryPrizeDeleteRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_entry = db.query(models.LotteryPrize).filter(models.LotteryPrize.rank_no == prizeData.rank_no).first()

    if not prev_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rank does not exist")
    
    db.delete(prev_entry)
    db.commit()

    allPrize = db.query(models.LotteryPrize).all()
    return allPrize


@router.get("/get_lottery_notice", response_model= schemas.LotteryNoticeRequestResponseModel)
def get_lottery_notice(db: Session = Depends(get_db)):
    notice = db.query(models.LotteryNoticeBoard).first()

    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notice found")
    
    return notice


@router.post("/modify_lottery_notice", response_model=schemas.HTTPError)
def modify_lottery_notice(noticeData : schemas.LotteryNoticeRequestResponseModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    notice = db.query(models.LotteryNoticeBoard).first()

    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notice found")
    
    notice.notice_text = noticeData.notice_text

    db.commit()

    return {"detail" : "Notice updated"}