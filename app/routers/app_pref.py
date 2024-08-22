from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/app",
    tags=["App"]
)

@router.get("/get_version_info", response_model= schemas.AppInfoResponseModel)
def get_version_info(db: Session = Depends(get_db)):
    version_data = db.query(models.AppPreferences).filter(models.AppPreferences.key == "version").first()

    if not version_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    
    return {"status": "success", "statusCode": 200, "message" : "Got app info", "data" : version_data}

