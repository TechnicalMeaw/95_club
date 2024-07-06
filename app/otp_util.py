# from fastapi import FastAPI
# from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
# from starlette.requests import Request
# from starlette.responses import JSONResponse
# from pydantic import EmailStr, BaseModel
# from typing import List
from random import randint
import requests
from .config import settings

def generate_otp():
    otp = randint(1001, 9999)
    return otp


def send_voice_otp(otp: int, phone: str):
    res = requests.get(f'{settings.voice_otp_base_url}?authorization={settings.sms_otp_auth_key}&route=otp&variables_values={otp}&numbers={phone}').json()
    print(res)
    return res['return'] == True


# conf = ConnectionConfig(
#     MAIL_USERNAME="Ja.adam192@gmail.com",
#     MAIL_PASSWORD="avhxhxwpiyosmjij",
#     MAIL_FROM = "Ja.adam192@gmail.com",
#     MAIL_PORT=465,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS = False,
#     MAIL_SSL_TLS = True,
#     USE_CREDENTIALS = True
# )


# async def sendOTP(email, otp: int):

#     message = MessageSchema(
#         subject="Your OTP",
#         recipients=email,  # List of recipients, as many as you can pass  
#         body='<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">'+
#             '<div style="margin:50px auto;width:70%;padding:20px 0">'+
#                 '<div style="border-bottom:1px solid #eee">'+
#                 '<a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Real Teenpatti</a>'+
#                 '</div>'+
#                 '<p style="font-size:1.1em">Hi,</p>'+
#                 '<p>Thank you for choosing Real Teenpatti. Use the following OTP to complete your Sign Up procedures. OTP is valid for 5 minutes</p>'+
#                 f'<h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{otp}</h2>'+
#                 '<p style="font-size:0.9em;">Regards,<br />Real Teenpatti</p>'+
#                 '<hr style="border:none;border-top:1px solid #eee" />'+
#                 '<div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">'+
#                 '<p>Real Teenpatti</p>'+
#                 '</div>'+
#             '</div>'+
#             '</div>',
#         subtype="html"
#     )

#     fm = FastMail(conf)
#     await fm.send_message(message)