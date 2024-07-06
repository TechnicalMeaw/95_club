from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix= "/lucky_draw",
    tags=["Lucky Draw"])


@router.get("/get_all_coin_values", response_model=List[schemas.LuckyDrawCoinValues])
def get_all_coin_values(db: Session = Depends(get_db)):
    all_coins = db.query(models.LuckyDrawCoinValues).order_by(models.LuckyDrawCoinValues.id).all()

    return all_coins

@router.post("/modify_coin_value")
def modify_coin_value(coinData : schemas.ModifyLuckyDrawCoinRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_coin = db.query(models.LuckyDrawCoinValues).filter(models.LuckyDrawCoinValues.id == coinData.id).first()

    if not prev_coin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="")
    
    prev_coin.coin_value = coinData.coin_value

    db.commit()

    return {"detail" : "Successfully updated coin value."}