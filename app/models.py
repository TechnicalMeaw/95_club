import enum
from sqlalchemy import Column, Enum, Integer, String, Boolean, TIMESTAMP, TextClause, ForeignKey, text
from .database import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable = False)
    phone_no = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))
    is_verified = Column(Boolean, nullable = False, server_default = TextClause("True"))
    role = Column(Integer, server_default = TextClause("1"))
    country_code = Column(String)
    refferal = Column(String, nullable = False, server_default=TextClause("gen_random_uuid()"))
    last_login = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("Now()"))
    is_deleted = Column(Boolean, nullable = False, server_default = text("False"))


class TempUsers(Base):
    __tablename__ = "temp_users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    phone_number = Column(String, nullable = False, index=True, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("Now()"))
    role = Column(Integer, server_default = text("1"))
    verified = Column(Boolean, nullable = False, server_default = text("False"))

class OTP(Base):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("Now()"))
    username = Column(String, nullable = False)
    otp = Column(String, nullable = False)
    otp_type = Column(String, nullable = False)
    is_used = Column(Boolean, nullable = False, server_default = text("False"))



class Refferals(Base):
    __tablename__ = "refferals"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    refferal_user_id = Column(Integer)
    reffered_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Integer, nullable = False, server_default = TextClause("10"))
    is_success = Column(Boolean, nullable = False, server_default = TextClause("True"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

    user = relationship("User")


class Coins(Base):
    __tablename__ = "coins"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False, unique = True)
    num_of_coins = Column(Integer, nullable = False, server_default = TextClause("0"))
    coin_type = Column(Integer, nullable=False, server_default= TextClause("1"))
    multiplication_factor = Column(Integer, nullable=False, server_default = TextClause("1"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


class BidColorOptions(enum.Enum):
    red = 'red'
    green = 'green'
    violet = 'violet'
    green_violet = 'green_violet'
    red_violet = 'red_violet'
    
# class BidNumberOptions(enum.Enum):
#     zero = 0
#     one = 1
#     two = 2
#     three = 3
#     four = 4
#     five = 5
#     six = 6
#     seven = 7
#     eight = 8
#     nine = 9

class BidSizeOptions(enum.Enum):
    big = 'big'
    small = 'small'

class GameLogs(Base):
    __tablename__ = "game_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    # 1 -> 30 sec
    # 2 -> 1 min
    # 3 -> 3 min
    # 4 -> 5 min
    game_type = Column(Integer, index=True, nullable=False)
    result_number = Column(Integer, nullable=True, index = True)
    result_color = Column(Enum(BidColorOptions), nullable=True, index=True)
    result_size = Column(Enum(BidSizeOptions), nullable=True, index=True)
    is_finished = Column(Boolean, nullable = False, server_default = TextClause("False"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

class UserBids(Base):
    __tablename__ = "user_bids"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    game_coin_price = Column(Integer, nullable = False, server_default = TextClause("10"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey('game_logs.id', ondelete="CASCADE"), nullable=False)
    bid_number = Column(Integer, nullable=True, index=True)
    bid_color = Column(Enum(BidColorOptions), nullable=True, index=True)
    bid_size = Column(Enum(BidSizeOptions), nullable=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))
    

class UserGameLogs(Base):
    __tablename__ = "user_game_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey('game_logs.id', ondelete="CASCADE"), nullable=False)
    win_coin_value = Column(Integer, nullable = True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

    game = relationship('GameLogs')



# class Transactions(Base):
#     __tablename__ = "transactions"
#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     amount = Column(Integer, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
#     transction_id = Column(String, nullable=False, unique=True)
#     isAdded = Column(Boolean, nullable  = False, server_default = TextClause("True"))
#     transaction_medium = Column(String)
#     is_verified = Column(Boolean, nullable = False, server_default=TextClause("False"))
#     is_rejected_by_admin = Column(Boolean, nullable = False, server_default = TextClause("False"))
#     screenshot_url = Column(String)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

#     user = relationship("User")



# class OTPs(Base):
#     __tablename__ = "otps"
#     user_email = Column(String, nullable = False, primary_key = True, unique= True)
#     otp = Column(Integer, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


# class Lottery(Base):
#     __tablename__ = "lottery"
#     lottery_token = Column(Integer, primary_key=True, unique= True, autoincrement=True)
#     is_winner = Column(Boolean, nullable=False, server_default = TextClause("False"))
#     user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable = False)
#     lottery_id = Column(Integer, server_default= TextClause("1"))
#     lottery_coin_price = Column(Integer, nullable = False, server_default = TextClause("20"))
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

#     user = relationship("User")

# class LotteryPrize(Base):
#     __tablename__ = "lottery_prize"
#     rank_no = Column(Integer, nullable=False, unique= True, primary_key = True)
#     prize_money = Column(Integer, nullable=False)

# class LotteryWinners(Base):
#     __tablename__ = "lottery_winners"
#     lottery_token_no = Column(Integer, primary_key= True, unique = True, nullable=False)
#     position = Column(Integer, ForeignKey("lottery_prize.rank_no", ondelete="CASCADE"), unique = True, nullable=False)
#     user_id =  Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False, unique = False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))
#     is_amount_credited = Column(Boolean, nullable = False, server_default=TextClause("False"))

#     user = relationship("User")

# class Withdrawals(Base):
#     __tablename__ = "withdrawals"
#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     phone_no = Column(String, nullable=False)
#     transaction_medium = Column(String, nullable=False)
#     amount = Column(Integer, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
#     is_verified = Column(Boolean, nullable = False, server_default=TextClause("False"))
#     is_rejected_by_admin = Column(Boolean, nullable = False, server_default = TextClause("False"))
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

#     user = relationship("User")

# class HorseRaceBids(Base):
#     __tablename__ = "horse_race_bids"

#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
#     horse_id = Column(Integer, nullable=False)
#     bid_amount = Column(Integer, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


# class TransactionMedium(Base):

#     __tablename__ = "transaction_mediums"

#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     medium_title = Column(String, nullable=False)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable = False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


# class LuckyDrawCoinValues(Base):
#     __tablename__ = "lucky_draw_coin_values"

#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     coin_value = Column(Integer, nullable=False)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable = False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))

# class LotteryNoticeBoard(Base):
#     __tablename__ = "lottery_notice"

#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     notice_text = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


# class NoticeBoard(Base):
#     __tablename__ = "all_notice"

#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     notice_text = Column(String, nullable=False)
#     # 1 for dashboard
#     notice_type = Column(Integer, nullable = False, server_default=TextClause("1"))
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))


# class JhandiMundaBids(Base):
#     __tablename__ = "jhandi_munda_bids"
#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
#     card_id = Column(Integer, nullable=False)
#     bid_amount = Column(Integer, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=TextClause("Now()"))
