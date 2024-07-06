from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.sql.expression import cast
from sqlalchemy import String

router = APIRouter(
    prefix= "/reffer",
    tags=["Refferals"]
)

@router.get("/get_my_refferals", response_model=List[schemas.RefferalResponse])
def get_all_users(db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    all_my_refferals = db.query(models.Refferals).filter(models.User.id == current_user.id).all()

    if not all_my_refferals:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refferals not found")
    
    return all_my_refferals

