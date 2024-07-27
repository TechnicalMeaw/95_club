from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def intro(request: Request):
    return templates.TemplateResponse("website.html", {"request": request})
