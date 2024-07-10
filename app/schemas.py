from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from . import models

# Create User Request Model
class UserCreate(BaseModel):
    name: str
    phone_no: str
    password: str
    email : Optional[str]
    refferal : Optional[str]

# User login response model
class UserOut(BaseModel):
    id: int
    name: str
    phone_no: str
    created_at : datetime

    class Config:
        from_attributes = True

# OTP
class SendOtpRequestModel(BaseModel):
    phone_number : str


class VerifyOTPRequestModel(BaseModel):
    otp: int
    phone_number: str
    otp_type: Optional[str] = 'voice'

class OTPResponseModel(BaseModel):
    status: bool
    detail: str


class UserOutWithRefferal(UserOut):
    refferal : str

    class Config:
        from_attributes = True


class UserOutWithCoin(BaseModel):
    User : UserOut
    coins : Optional[int]

    class Config:
        from_attributes = True

# User login request model
class UserLogin(BaseModel):
    phone_no : str
    password : str

# Token response model
class Token(BaseModel):
    token : str
    existing_user : bool
    login_flow_completed : bool

# For token verification
class TokenData(BaseModel):
    id : Optional[str] = None


# Model for error messege
class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException string / Success string"},
        }

# Model for coin updation request
class CoinUpdateRequest(BaseModel):
    coins : int
    updation_type : str


class CoinResponse(BaseModel):
    num_of_coins: int
    coin_type: int

    class Config:
        from_attributes = True

# For transaction request
class TransactionRequest(BaseModel):
    amount : int
    transction_id : str
    isAdded : bool
    transaction_medium : str
    screenshot_url : str

# For transaction verification request --- Admin Panel
class VerifyTransactionRequest(BaseModel):
    user_id : int
    transaction_id : str
    in_app_transaction_id : int
    is_verified : bool


#  Individualtransaction response
class IndividualTransactionResponse(BaseModel):
    id : int
    amount : int
    transction_id : str
    isAdded : bool
    transaction_medium : str
    is_verified : bool
    is_rejected_by_admin : bool
    screenshot_url : str
    created_at : datetime

    class Config:
        from_attributes = True


# All transaction response
class Transaction(IndividualTransactionResponse):
    user_id : int
    user : UserOut

    class Config:
        from_attributes = True


# Withdraw
class WithdrawRequest(BaseModel):
    phone_no : str
    transaction_medium : str
    amount : int

class VerifyWithdrawRequest(BaseModel):
    withdraw_id : int
    is_verified : bool


class WithdrawIndividualResponse(BaseModel):
    id : int
    amount : int
    phone_no : str
    transaction_medium : str
    is_verified : bool
    is_rejected_by_admin : bool
    created_at : datetime

    class Config:
        from_attributes = True


class WithdrawResponse(WithdrawIndividualResponse):
    user_id : int
    user : UserOut

    class Config:
        from_attributes = True


# Send Otp request
class EmailSchema(BaseModel):
   email: List[EmailStr]

# verify Otp
class OtpVerifyRequest(BaseModel):
    phone: str

class ChangePasswordRequest(BaseModel):
    phone_no : str
    newPassword: str


class LotteryOutResponse(BaseModel):
    lottery_token: int
    is_winner : bool
    user : UserOut

    class Config:
        from_attributes = True

# Lottery Buy Response
class BuyLotteryRequest(BaseModel):
    amount: int
    timeZoneOffsetFromUtc : Optional[int]


class TimeLeftResponse(BaseModel):
    time_left_in_millis : str

    class Config:
        from_attributes = True


class LotteryWinner(BaseModel):
    lottery_token_no : int
    position : int

    user : UserOut

    class Config:
        from_attributes = True


class SetLotteryWinnerRequest(BaseModel):
    token: int
    rank: int

class RemoveLotteryWinnerRequest(BaseModel):
    token: int


# Lottery Prize
class LotteryPrize(BaseModel):
    rank_no : int
    prize_money : int

    class Config:
        from_attributes = True


class LotteryPrizeDeleteRequest(BaseModel):
    rank_no: int


# Refferal response
class RefferalResponse(BaseModel):
    User : UserOut
    reffered_user_id : int
    amount : int
    is_success : bool
    created_at : datetime

    class Config:
        from_attributes = True


class HorseMatchTiming(BaseModel):

    is_horse_bidding_slot_open : bool
    remaining_time_in_millis : int


class HorseRaceWinnerResponseModel(BaseModel):
    bid_amount : Optional[int]

    class Config:
        from_attributes = True

class HorseRaceWinnerDetailsResponseModel(BaseModel):
    winnig_horse_id : int
    is_user_winner : bool
    total_bid_money : int
    bid_on_winning_horse : int = 0
    win_money : int = 0

    class Config:
        from_attributes = True


class HorseRaceBidRequestModel(BaseModel):
    bid_horse_id : int
    bid_amount : int


class HorseRaceMyBidsResponseModel(BaseModel):
    horse_id : int
    bid_amount : int

    class Config:
        from_attributes = True


# Request Model
class AddTransactionMediumRequestModel(BaseModel):
    medium_title : str

#  Response Model
class TransactionMedium(BaseModel):
    id : int
    medium_title : str
    created_at : datetime

    class Config:
        from_attributes = True

# Delete Request Model
class DeleteTransactionMediumRequestModel(BaseModel):
    id : int


#  Response Model
class LuckyDrawCoinValues(BaseModel):
    id : int
    coin_value : int
    created_at : datetime

    class Config:
        from_attributes = True

# Modify Request Model
class ModifyLuckyDrawCoinRequestModel(BaseModel):
    id : int
    coin_value : int
    


class LotteryNoticeRequestResponseModel(BaseModel):
    notice_text : str

    class Config:
        from_attributes = True


class JhandiMundaTiming(BaseModel):

    is_jhandi_munda_slot_open : bool
    remaining_time_in_millis : float


class JhandiMundaBidRequestModel(BaseModel):
    bid_card_id : int
    bid_amount : int


class JhandiMundaWinnerDetailsResponseModel(BaseModel):
    winnig_card_id : int
    is_user_winner : bool
    total_bid_money : int
    bid_on_winning_card : int = 0
    win_money : int = 0

    class Config:
        from_attributes = True


class JhandiMundaMyBidsResponseModel(BaseModel):
    card_id : int
    bid_amount : int

    class Config:
        from_attributes = True



# Common
# ---------
# Response model
class CommonResponseModel(BaseModel):
    status : str
    statusCode : int
    message : str 

class PaginationResponseModel(BaseModel):
    total_count: int
    current_page : int
    total_page : int
    prev_page : int | None
    next_page: int | None


# Game Play
# ---------------------------------------------------------
class GamePlayBidRequestModel(BaseModel):
    game_id : int
    bid_number : Optional[int] = None
    bid_color : Optional[models.BidColorOptions] = None
    bid_size : Optional[models.BidSizeOptions] = None
    bid_amount : int

# Game History
class GameHistory(BaseModel):
    id : int
    result_number : int
    result_color : str
    result_size : str
    created_at : datetime
    class Config:
        from_attributes = True

class GameHistoryResponseModel(CommonResponseModel, PaginationResponseModel):
    data : List[GameHistory]


class MyGameHistory(BaseModel):
    # id: int
    # user_id : int
    game_id: int
    win_coin_value : int
    created_at: datetime
    game : GameHistory
    class Config:
        from_attributes = True
class MyGameHistoryResponseModel(CommonResponseModel, PaginationResponseModel):
    data: List[MyGameHistory]