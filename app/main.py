from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import user, auth, gameplay, coins, transactions, webpage
# lottery, withdraw, refferals, horse_race, lucky_draw, notice_board, jhandi_munda


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Webpage
app.include_router(webpage.router)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(gameplay.router)

app.include_router(coins.router)
app.include_router(transactions.router)
# app.include_router(lucky_draw.router)
# app.include_router(lottery.router)
# app.include_router(withdraw.router)
# app.include_router(refferals.router)
# app.include_router(horse_race.router)
# app.include_router(notice_board.router)
# app.include_router(jhandi_munda.router)