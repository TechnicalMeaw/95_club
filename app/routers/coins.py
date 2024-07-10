from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/coin",
    tags=["Coins"]
)


# @router.post("/", response_model=schemas.CoinResponse, responses={status.HTTP_200_OK: {"model" : schemas.CoinResponse}, 
#                         status.HTTP_403_FORBIDDEN : {"model": schemas.HTTPError,"description": "If coin balance is not as per requirments"},
#                         status.HTTP_404_NOT_FOUND : {"model": schemas.HTTPError,"description": "When coin balance or User does not exists"}})
# def update_coin(coinRequest: schemas.CoinUpdateRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
#     user = db.query(models.User).filter(models.User.id == current_user.id).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exists")
    
#     coin_balance_query = db.query(models.Coins).filter(models.Coins.user_id == current_user.id)
    
#     if coinRequest.updation_type == "add":
#         user_coin_balance = coin_balance_query.first()

#         if not user_coin_balance:
#             new_coin_balance = schemas.CoinResponse(num_of_coins=coinRequest.coins, coin_type=1)
#             new_coins_row = models.Coins(**new_coin_balance.dict())
#             new_coins_row.user_id = current_user.id
#             db.add(new_coins_row)
#             db.commit()
#             return new_coin_balance
        

#         user_coin_balance.num_of_coins += coinRequest.coins

#         db.commit()
#         return user_coin_balance
    
#     else:
#         user_coin_balance = coin_balance_query.first()
    
#         if not user_coin_balance:
#            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coin balance not found")

#         if user_coin_balance.num_of_coins < coinRequest.coins:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin balance not enough")

#         user_coin_balance.num_of_coins -= coinRequest.coins

#         db.commit()
#         return user_coin_balance
    
    
@router.get("/", response_model=schemas.CoinResponse)
def get_coin_balance(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    coin_balance = db.query(models.Coins).filter(models.Coins.user_id == current_user.id).first()

    if not coin_balance:
        coins = schemas.CoinResponse(num_of_coins=0, coin_type=0)

        return coins
    
    return coin_balance