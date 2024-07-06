from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix= "/transaction",
    tags=["Transaction"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.HTTPError)
def transact(transactionData : schemas.TransactionRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prevTransactionOnSameId = db.query(models.Transactions).filter(models.Transactions.user_id == current_user.id, models.Transactions.transction_id == transactionData.transction_id).first()

    if prevTransactionOnSameId:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transaction id already exists")
    
    new_transaction = models.Transactions(user_id = current_user.id, **transactionData.dict())
    db.add(new_transaction)
    db.commit()

    return {"detail": "Transaction added, need to be verified"}


@router.post("/verify")
def verify_transaction(verificationData: schemas.VerifyTransactionRequest, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    transaction = db.query(models.Transactions).filter(models.Transactions.user_id == verificationData.user_id).filter(models.Transactions.transction_id == verificationData.transaction_id).filter(models.Transactions.id == verificationData.in_app_transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transaction does not exists")
    
    # Get prev balance
    coin_balance_query = db.query(models.Coins).filter(models.Coins.user_id == verificationData.user_id)
    user_coin_balance = coin_balance_query.first()
    
    if verificationData.is_verified:
        transaction.is_verified = True
        
        # Update the coin balance
        if not user_coin_balance:
            new_coin_balance = schemas.CoinResponse(num_of_coins=transaction.amount, coin_type=1)
            new_coins_row = models.Coins(**new_coin_balance.dict())
            new_coins_row.user_id = transaction.user_id
            db.add(new_coins_row)
            db.commit()
            return new_coin_balance
        

        user_coin_balance.num_of_coins += transaction.amount

        db.commit()
        return user_coin_balance
    
    else:
        transaction.is_verified = False
        transaction.is_rejected_by_admin = True
        db.commit()

        # Get coin balance
        new_coin_balance = schemas.CoinResponse(num_of_coins=transaction.amount, coin_type=1)
        new_coins_row = models.Coins(**new_coin_balance.dict())
        new_coins_row.user_id = transaction.user_id

        return new_coin_balance

    
@router.get("/all_transactions", response_model=List[schemas.Transaction])
def get_all_transactions(pageNo : int = 1, search_transaction_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    user_entries = db.query(models.Transactions).filter(models.Transactions.transction_id.contains(search_transaction_id)).order_by(0-models.Transactions.id).limit(10).offset((pageNo-1)*10).all()

    if not user_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Transactions not found")
    
    return user_entries


@router.get("/my_transactions", response_model=List[schemas.IndividualTransactionResponse])
def get_all_transactions(pageNo : int = 1, search_transaction_id: Optional[str] = "", db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):

    user_entries = db.query(models.Transactions).filter(models.Transactions.user_id == current_user.id).filter(models.Transactions.transction_id.contains(search_transaction_id)).order_by(0-models.Transactions.id).limit(10).offset((pageNo-1)*10).all()

    if not user_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Transactions not found")
    
    return user_entries


@router.get("/get_all_transaction_mediums", response_model=List[schemas.TransactionMedium])
def get_all_transaction_mediums(db: Session = Depends(get_db)):
    all_mediums = db.query(models.TransactionMedium).all()

    return all_mediums

@router.post("/add_transaction_medium", response_model = schemas.HTTPError, status_code = status.HTTP_201_CREATED)
def add_transaction_medium(transactionMediumData : schemas.AddTransactionMediumRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    new_entry = models.TransactionMedium(created_by = current_user.id, **transactionMediumData.dict())
    db.add(new_entry)
    db.commit()
    return {"detail": "Successfully added medium"}


@router.post("/delete_transaction_medium", response_model= schemas.HTTPError)
def delete_transaction_medium(deleteData : schemas.DeleteTransactionMediumRequestModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    prev_entry_query = db.query(models.TransactionMedium).filter(models.TransactionMedium.id == deleteData.id, models.TransactionMedium.created_by == current_user.id)
    prev_entry = prev_entry_query.first()

    if not prev_entry:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Medium not found")
    
    prev_entry_query.delete(synchronize_session=False)
    db.commit()

    return {"detail": "Successfully deleted medium"}

    
    