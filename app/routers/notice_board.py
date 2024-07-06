from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/Notice",
    tags=["Notice"]
)

@router.get("/get_dashboard_notice", response_model= schemas.LotteryNoticeRequestResponseModel)
def get_lottery_notice(db: Session = Depends(get_db)):
    notice = db.query(models.NoticeBoard).filter(models.NoticeBoard.notice_type == 1).first()

    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notice found")
    
    return notice


@router.post("/modify_dashboard_notice", response_model=schemas.HTTPError)
def modify_lottery_notice(noticeData : schemas.LotteryNoticeRequestResponseModel, db: Session = Depends(get_db), current_user : models.User = Depends(oauth2.get_current_user)):
    notice = db.query(models.NoticeBoard).filter(models.NoticeBoard.notice_type == 1).first()

    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notice found")
    
    notice.notice_text = noticeData.notice_text

    db.commit()

    return {"detail" : "Notice updated"}