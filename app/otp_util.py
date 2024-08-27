# from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
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


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM = settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
)


async def send_email_otp(email, otp: int):

    message = MessageSchema(
    subject="Your OTP for 95 Club",
    recipients=email,  # List of recipients
    body=f'''
    <div style="font-family: Helvetica, Arial, sans-serif; width: 100%; overflow: auto; line-height: 1.8; color: #333;">
        <div style="margin: 40px auto; width: 70%; padding: 20px; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <a href="" style="font-size: 1.6em; color: #ff6600; text-decoration: none; font-weight: 700;">95 Club</a>
            </div>
            <p style="font-size: 1.2em; margin-top: 20px;">Hi,</p>
            <p style="font-size: 1.1em;">Thank you for joining 95 Club! Use the following OTP to complete your sign-up process. The OTP is valid for 5 minutes.</p>
            <div style="text-align: center;">
                <h2 style="background: #ff6600; display: inline-block; margin: 20px 0; padding: 10px 20px; color: #fff; border-radius: 5px;">{otp}</h2>
            </div>
            <p style="font-size: 1em;">Regards,<br />95 Club Team</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
            <div style="color: #aaa; font-size: 0.9em; line-height: 1.2; font-weight: 300;">
                <p>95 Club</p>
                <p>Your gateway to earning money.</p>
            </div>
        </div>
    </div>
    ''',
    subtype="html"
    )



    fm = FastMail(conf)
    await fm.send_message(message)

# import boto3
# from botocore.exceptions import NoCredentialsError, ClientError

# # Set up your AWS credentials
# ses_client = boto3.client(
#     'ses',
#     region_name='ap-south-1',  # e.g., 'us-east-1'
#     aws_access_key_id='your-access-key-id',
#     aws_secret_access_key='your-secret-access-key'
# )

# def send_otp_email(recipient_email, otp_code):
#     try:
#         response = ses_client.send_email(
#             Source='your-verified-email@example.com',
#             Destination={
#                 'ToAddresses': [recipient_email],
#             },
#             Message={
#                 'Subject': {
#                     'Data': 'Your OTP Code',
#                 },
#                 'Body': {
#                     'Text': {
#                         'Data': f'Your OTP code is {otp_code}. It is valid for 10 minutes.',
#                     },
#                 },
#             }
#         )
#         return response
#     except (NoCredentialsError, ClientError) as e:
#         print(f"Error sending email: {e}")
#         return None
