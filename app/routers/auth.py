from typing import Optional
from fastapi import status, HTTPException, Depends, APIRouter
from datetime import datetime, timedelta

# from app.otp_util import generateOtp, sendOTP
from .. import models, schemas, utils, oauth2, otp_util
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone_no == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="First verify your phone number")
    
    # create a token
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"token": access_token, "existing_user" : True, "login_flow_completed": True}



# @router.post("/change_password")
# def change_password(password_data: schemas.ChangePasswordRequest, db: Session = Depends(get_db)):
#     country_code, number = utils.split_phone_number(password_data.phone_no)

#     db_user = db.query(models.User).filter(models.User.phone_no == number).filter(models.User.country_code == country_code).first()

#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exists")

#     db_user.password = utils.hash(password_data.newPassword)
#     db.commit()

#     # create a token
#     access_token = oauth2.create_access_token(data={"user_id": db_user.id})
#     return {"access_token": access_token, "token_type": "bearer"}




# @router.get("/send_otp", response_model=schemas.OTPResponseModel)
# async def send_otp(username: str, otp_type: Optional[str] = 'sms', db: Session = Depends(get_db)):
#     if utils.is_phone_number(username):

#         otp_generated = otp_util.generate_new_otp()
#         _, phone = utils.split_phone_number(username)
#         is_otp_sent = False
#         # if otp_type == 'sms':
#         #     is_otp_sent = otp_util.send_sms_otp(otp_generated, phone)
#         # else:
#         is_otp_sent = otp_util.send_voice_otp(otp_generated, phone)
        
#         if not is_otp_sent:
#             raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="There are some problems sending OTP, please try again in some time.")

#         new_otp = models.OTP(otp=str(otp_generated), username=username, customer_id=local_user.id, firebase_uid=local_user.firebase_uid, otp_type=otp_type)
#         db.add(new_otp)
#         db.commit()
#         return {"status": True, "detail": "OTP has been sent successfully"}

#     # elif utils.is_email(username):
#     #     user = firebase_auth.get_firebase_user_from_email(username)
#     #     if not user:
#     #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It seems like you don't have an account with this email.")

#     #     local_user = db.query(models.User).filter(models.User.firebase_uid == user['_data']['localId'], models.User.is_deleted==False).first()
#     #     if not local_user:
#     #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It seems like you've never explored the plantonic application before with this phone number.")

#     #     otp_generated = utils.generate_new_otp()
#     #     await otp_utils.send_email_otp(otp_generated, username, user['_data']['displayName'].split(' ')[0])

#     #     new_otp = models.OTP(otp=str(otp_generated), username=username, customer_id=local_user.id, firebase_uid=local_user.firebase_uid, otp_type='email')
#     #     db.add(new_otp)
#     #     db.commit()
#     #     return JSONResponse(content=jsonable_encoder({"status": True, "detail": "OTP has been sent successfully"}), status_code=status.HTTP_200_OK)
#     else:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You've entered an invalid username.")


@router.post("/send_otp")
def send_otp(request_data : schemas.SendOtpRequestModel, db: Session = Depends(get_db)):

    if not request_data.phone_number or not utils.is_phone_number(request_data.phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter valid phone number")
    
    _, number = utils.split_phone_number(request_data.phone_number)

    otp_generated = otp_util.generate_otp()
    is_otp_sent = otp_util.send_voice_otp(otp_generated, number)
        
    if not is_otp_sent:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="There are some problems sending OTP, please try again in some time.")

    new_otp = models.OTP(otp=str(otp_generated), username=request_data.phone_number, otp_type='sms')
    db.add(new_otp)
    db.commit()

    return {"status": "success", "statusCode": 200, "message" : "OTP sent"}


@router.post("/verify_otp", response_model= schemas.Token)
def verify_otp(verify_request: schemas.VerifyOTPRequestModel, db: Session = Depends(get_db)):
    existing_otp = db.query(models.OTP).filter(models.OTP.username == verify_request.phone_number, models.OTP.created_at >= datetime.utcnow() - timedelta(minutes=5)).order_by(models.OTP.created_at.desc()).first()
    print(existing_otp)
    if not existing_otp or existing_otp.is_used:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You've entered an invalid OTP.")

    if existing_otp.otp != str(verify_request.otp):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You've entered a wrong OTP.")

    # OTP verified
    existing_otp.is_used = True
    db.commit()

    # Check if account already exists
    if utils.is_phone_number(verify_request.phone_number):
        existing_user = db.query(models.User).filter(models.User.phone_no == verify_request.phone_number, models.User.is_deleted==False).first()
        if existing_user:
            new_token = oauth2.create_access_token(data=existing_user.id)
            return {"token": new_token, "existing_user" : True, "login_flow_completed": True}
        
        else:
            existing_temp_user = db.query(models.TempUsers).filter(models.TempUsers.phone_number == verify_request.phone_number).first()
            if existing_temp_user:
                new_token = oauth2.create_access_token(data=existing_temp_user.id)
                return {"token": new_token, "existing_user" : True, "login_flow_completed": False}
            else:
                new_temp_user = models.TempUsers(phone_number = verify_request.phone_number)
                db.add(new_temp_user)
                db.commit()
                new_token = oauth2.create_access_token(data=new_temp_user.id)
                return {"token": new_token, "existing_user" : False, "login_flow_completed": False}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")

