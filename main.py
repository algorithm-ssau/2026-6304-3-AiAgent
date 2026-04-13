from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from llm_client import classify_with_yandex_gpt
from logger import log_request, get_history

app = FastAPI(title="ИИ-агент техподдержки")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/classify")
async def classify(user_message: str = Form(...)):
    result = classify_with_yandex_gpt(user_message)
    # Логируем запрос и ответ
    log_request(user_message, result)
    return result

@app.get("/history", response_class=HTMLResponse)
async def show_history(request: Request):
    history = get_history(limit=50)
    return templates.TemplateResponse("history.html", {"request": request, "history": history})