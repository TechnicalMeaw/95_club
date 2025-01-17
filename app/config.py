from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_days: int
    voice_otp_base_url: str
    sms_otp_auth_key: str
    aes_key : str
    iv : str
    mail_username : str
    mail_password : str
    mail_from : str
    mail_port : int
    mail_server : str


    class Config:
        env_file = ".env"

settings = Settings()