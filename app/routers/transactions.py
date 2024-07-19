import math
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix= "/transaction",
    tags=["Transaction"]
)

@router.post("/deposit_request", status_code=status.HTTP_201_CREATED, response_model=schemas.HTTPError)
def deposit(transaction_data : schemas.TransactionRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_transaction_on_same_id = db.query(models.Transactions).filter(models.Transactions.transction_id == transaction_data.transction_id).first()

    if prev_transaction_on_same_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transaction id already exists")
    
    new_transaction = models.Transactions(user_id = current_user.id, **transaction_data.__dict__)
    db.add(new_transaction)
    db.commit()

    return {"detail": "Transaction added, need to be verified"}


@router.post("/withdraw_request", status_code=status.HTTP_201_CREATED, response_model=schemas.HTTPError)
def withdraw(withdraw_data : schemas.WithdrawRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    coin_balance = db.query(models.Coins).filter(current_user.id == models.Coins.user_id).first()

    if not coin_balance:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin Balance is not enough")
    
    if int(coin_balance.num_of_coins) < withdraw_data.amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coin Balance is not enough")
    
    if not withdraw_data.upi_id or not withdraw_data.account_number and not withdraw_data.ifsc_code and not withdraw_data.account_holder_name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid withdraw details")
    
    if withdraw_data.upi_id and not withdraw_data.account_number and not withdraw_data.ifsc_code and not withdraw_data.account_holder_name:
        # UPI transaction request
        new_withdraw_request_entry = models.Transactions(amount = withdraw_data.amount,
                                                          user_id = current_user.id,
                                                            is_added = False, 
                                                            transaction_medium = "UPI", 
                                                            receiver_details = withdraw_data.upi_id,
                                                        )    
        db.add(new_withdraw_request_entry)
        # Deduct coin balance
        coin_balance.num_of_coins -= withdraw_data.amount  
        db.commit()
        return {"detail": "Withdraw request with UPI transfer added, please wait until processed"}
    
    elif withdraw_data.account_number and withdraw_data.ifsc_code and withdraw_data.account_holder_name and not withdraw_data.upi_id:
        # Bank transaction request
        new_withdraw_request_entry = models.Transactions(amount = withdraw_data.amount,
                                                          user_id = current_user.id,
                                                            is_added = False, 
                                                            transaction_medium = "Bank", 
                                                            receiver_details = f"Account Number - {withdraw_data.account_number}, IFSC - {withdraw_data.ifsc_code}, Account Holder Name - {withdraw_data.account_holder_name}",
                                                        )    
        db.add(new_withdraw_request_entry)
        # Deduct coin balance
        coin_balance.num_of_coins -= withdraw_data.amount  
        db.commit()
        return {"detail": "Withdraw request with bank transfer added, please wait until processed"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid withdraw details")



@router.post("/verify", response_model=schemas.CoinResponse)
def verify_transaction(verification_data: schemas.VerifyTransactionRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    if current_user.role != 2 or current_user.role != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can verify transactions")
    
    transaction = db.query(models.Transactions).filter(models.Transactions.user_id == verification_data.user_id).filter(models.Transactions.id == verification_data.in_app_transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transaction does not exists")
    
    # Get prev balance
    coin_balance_query = db.query(models.Coins).filter(models.Coins.user_id == verification_data.user_id)
    user_coin_balance = coin_balance_query.first()
    
    if verification_data.is_verified:
        transaction.is_verified = True
        
        # If money add request 
        if transaction.is_added:
            # and coin balance is zero
            # Update the coin balance
            if not user_coin_balance:
                new_coin_balance = schemas.CoinResponse(num_of_coins=transaction.amount, coin_type=1)
                new_coins_row = models.Coins(**new_coin_balance.__dict__)
                new_coins_row.user_id = transaction.user_id
                db.add(new_coins_row)
                db.commit()
                return new_coin_balance
        
            # Update the coin balance
            user_coin_balance.num_of_coins += transaction.amount

        db.commit()
        return user_coin_balance
    
    else:
        transaction.is_verified = False
        transaction.is_rejected = True
        
        # If withdraw request rejected, then refund the balance
        # [Unlikely to happen]
        if not transaction.is_added:
            user_coin_balance.num_of_coins += transaction.amount

        db.commit()

        # Get coin balance
        new_coin_balance = schemas.CoinResponse(num_of_coins=transaction.amount, coin_type=1)
        new_coins_row = models.Coins(**new_coin_balance.__dict__)
        new_coins_row.user_id = transaction.user_id

        return new_coin_balance

    
@router.get("/all_transactions", response_model=schemas.AllTransactionsResponseModel)
def get_all_transactions(page_no : int = 1, search_transaction_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    transactions_query = db.query(models.Transactions).filter(models.Transactions.transction_id.contains(search_transaction_id)).order_by(0-models.Transactions.id)

    
    total_count = transactions_query.count() 
    total_page = math.ceil(total_count/10)
   
    transactions_data = transactions_query.limit(10).offset((page_no-1)*10).all()

    return {"status": "success", "statusCode": 200, "message" : "Successfully got all transaction history", 
            "total_count": total_count,
            "current_page": page_no,
            "total_page": total_page,
            "prev_page": page_no-1 if page_no > 1 else None, 
            "next_page": page_no+1 if page_no < total_page else None,
            "data" : transactions_data}


@router.get("/my_transactions", response_model=schemas.AllTransactionsResponseModel)
def get_all_transactions(page_no : int = 1, search_transaction_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    transactions_query = db.query(models.Transactions).filter(models.Transactions.user_id == current_user.id, models.Transactions.transction_id.contains(search_transaction_id)).order_by(0-models.Transactions.id)

    
    total_count = transactions_query.count() 
    total_page = math.ceil(total_count/10)
   
    transactions_data = transactions_query.limit(10).offset((page_no-1)*10).all()

    return {"status": "success", "statusCode": 200, "message" : "Successfully got my transaction history", 
            "total_count": total_count,
            "current_page": page_no,
            "total_page": total_page,
            "prev_page": page_no-1 if page_no > 1 else None, 
            "next_page": page_no+1 if page_no < total_page else None,
            "data" : transactions_data}


# @router.get("/get_all_transaction_mediums", response_model=List[schemas.TransactionMedium])
# def get_all_transaction_mediums(db: Session = Depends(get_db)):
#     all_mediums = db.query(models.TransactionMedium).all()

#     return all_mediums

# @router.post("/add_transaction_medium", response_model = schemas.HTTPError, status_code = status.HTTP_201_CREATED)
# def add_transaction_medium(transactionMediumData : schemas.AddTransactionMediumRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
#     new_entry = models.TransactionMedium(created_by = current_user.id, **transactionMediumData.dict())
#     db.add(new_entry)
#     db.commit()
#     return {"detail": "Successfully added medium"}


# @router.post("/delete_transaction_medium", response_model= schemas.HTTPError)
# def delete_transaction_medium(deleteData : schemas.DeleteTransactionMediumRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
#     prev_entry_query = db.query(models.TransactionMedium).filter(models.TransactionMedium.id == deleteData.id, models.TransactionMedium.created_by == current_user.id)
#     prev_entry = prev_entry_query.first()

#     if not prev_entry:
#         raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Medium not found")
    
#     prev_entry_query.delete(synchronize_session=False)
#     db.commit()

#     return {"detail": "Successfully deleted medium"}

    
    