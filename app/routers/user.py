from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.sql.expression import cast
from sqlalchemy import String, func

router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.Token,
             responses={status.HTTP_201_CREATED: {"model" : schemas.Token}, 
                        status.HTTP_403_FORBIDDEN : {"model": schemas.HTTPError,"description": "If user already exists"}})
async def create_user(user : schemas.UserCreate, db: Session = Depends(get_db), current_temp_user : models.TempUsers = Depends(oauth2.get_current_temp_user)):

    if current_temp_user.username != user.email or not utils.is_email(user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email")
    
    if user.phone_no and not utils.is_phone_number(user.phone_no):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")
    
    country_code, number = utils.split_phone_number(user.phone_no)

    # Check if user already exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")

    # if not country_code or not number:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid phone number")

    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    user.phone_no = number

    new_refferal_code = utils.generate_unique_referral_code(user.phone_no)

    new_user = models.User(country_code = country_code, 
                           name = user.name, 
                           phone_no = user.phone_no, 
                           password = user.password, 
                           email = user.email,
                           refferal = new_refferal_code)
    db.add(new_user)
    current_temp_user.verified = True
    db.commit()
    db.refresh(new_user)

    # TODO ("Remove later on production")
    # initial_coin_balance = models.Coins(user_id = new_user.id, num_of_coins = 0)
    # db.add(initial_coin_balance)
    # db.commit()

    if user.refferal != None and len(user.refferal) > 1:
        refferal_user = db.query(models.User).filter(models.User.refferal == user.refferal).first()
        
        if refferal_user:

            # # Update coin balance
            # coin_balance_query = db.query(models.Coins).filter(models.Coins.user_id == refferal_user.id)

            # user_coin_balance = coin_balance_query.first()

            # if not user_coin_balance:
            #     new_coin_balance = schemas.CoinResponse(num_of_coins=10, coin_type=1)
            #     new_coins_row = models.Coins(**new_coin_balance.dict())
            #     new_coins_row.user_id = refferal_user.id
            #     db.add(new_coins_row)            

            # user_coin_balance.num_of_coins += 10

            # Update new entry to refferal table
            # Just adding the user to refferal
            new_refferal_entry = models.Refferals(refferal_user_id = refferal_user.id, reffered_user_id = new_user.id, amount = 0)
            db.add(new_refferal_entry)
            db.commit()

    new_token = oauth2.create_access_token(data=new_user.id)

    return {"token": new_token, "existing_user" : True, "login_flow_completed": True}


# @router.get("/get_all_user_info", response_model=List[schemas.UserOutWithCoin])
# def get_all_users(page_no : int = 1, search_phone_number: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
#     query = db.query(models.User, models.Coins.num_of_coins.label("coins")).join(models.Coins, models.User.id == models.Coins.user_id, isouter=True).filter(cast(models.User.phone_no, String).contains(search_phone_number)).limit(10).offset((page_no-1)*10)


#     all_users = query.all()

#     if not all_users:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
#     return all_users


@router.get("/", response_model= schemas.UserOutWithRefferal)
def get_current_user(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User does not exist")
    
    total_ammount_added = db.query(func.sum(models.Transactions.amount)).filter(models.Transactions.user_id == current_user.id, models.Transactions.is_added == True).scalar() or 0
    total_commission_added = db.query(func.sum(models.Transactions.commission)).filter(models.Transactions.user_id == current_user.id, models.Transactions.is_added == True).scalar() or 0

    data = {
        "is_refferal_enabled" : total_ammount_added + total_commission_added >= 100,
        **user.__dict__
    }

    return data


# @router.get("/{id}", response_model= schemas.UserOut)
# def get_user(id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == id).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User with id: {id} does not exist")
    
#     return user




@router.post("/submit_feedback", response_model= schemas.CommonResponseModel)
def submit_feedback(request_data : schemas.FeedbackRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    new_feedback = models.Feedback(user_id = current_user.id, mobile_number = request_data.mobile_number, concern = request_data.concern)

    db.add(new_feedback)
    db.commit()
    return {"status": "success", "statusCode": 201, "message" : "Concern captured"}
