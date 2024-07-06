from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.sql.expression import cast
from sqlalchemy import String


router = APIRouter(
    prefix= "/withdraw",
    tags=["Withdrawals"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.HTTPError)
def withdraw(withdrawRequest : schemas.WithdrawRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    
    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin Balance is not enough")
    
    if int(coin_balance.num_of_coins) < withdrawRequest.amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin Balance is not enough")

    new_withdraw_request_entry = models.Withdrawals(amount = withdrawRequest.amount, user_id = current_user.id, phone_no = withdrawRequest.phone_no, transaction_medium = withdrawRequest.transaction_medium)    
    db.add(new_withdraw_request_entry)    
    coin_balance.num_of_coins -= withdrawRequest.amount
    db.commit()

    return {"detail": "Withdraw request added, please wait until processed"}


@router.post("/verify")
def verify_withdraw(verificationData: schemas.VerifyWithdrawRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    withdraw_request = db.query(models.Withdrawals).filter(models.Withdrawals.id == verificationData.withdraw_id).first()
    
    if not withdraw_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Withdraw request not found")
    
    if verificationData.is_verified:
        withdraw_request.is_verified = True
        db.commit()

        return {"details": "Withdraw request sucessfully processed"}
    
    coin_balance = db.query(models.Coins).filter(withdraw_request.user_id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Request not allowed")
    
    verificationData.is_rejected_by_admin = True
    coin_balance.num_of_coins = coin_balance.num_of_coins + withdraw_request.amount
    db.commit()

    return {"details": "Withdraw request sucessfully processed"}



@router.get("/all_requests", response_model=List[schemas.WithdrawResponse])
def get_all_transactions(page_no : int = 1, search_withdraw_request_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    user_entries = db.query(models.Withdrawals).filter(cast(models.Withdrawals.id, String).contains(search_withdraw_request_id)).order_by(0-models.Withdrawals.id).limit(10).offset((page_no-1)*10).all()

    if not user_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No withdraw requests has been made")
    
    return user_entries



@router.get("/my_requests", response_model=List[schemas.WithdrawIndividualResponse])
def get_all_transactions(page_no : int = 1, search_withdraw_request_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    user_entries = db.query(models.Withdrawals).filter(models.Withdrawals.user_id == current_user.id).filter(cast(models.Withdrawals.id, String).contains(search_withdraw_request_id)).order_by(0-models.Withdrawals.id).limit(10).offset((page_no-1)*10).all()

    if not user_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No withdraw requests has been made")
    
    return user_entries