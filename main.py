from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="ИИ-агент техподдержки")
templates = Jinja2Templates(directory="templates")

# Модель для ответа (пока заглушка)
class ClassificationResponse(BaseModel):
    category: str
    priority: str
    explanation: str

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    """Отображает HTML-форму для ввода обращения"""
    return templates.TemplateResponse("index.html", {})  # request не используется в HTML

@app.post("/classify", response_model=ClassificationResponse)
async def classify(request: Request, user_message: str = Form(...)):
    """
    Временная заглушка. Позже заменим на вызов LLM.
    Всегда возвращает тестовую категорию и приоритет.
    """
    # Здесь потом будет реальная логика с ИИ
    return ClassificationResponse(
        category="test",
        priority="low",
        explanation="Это временная заглушка. Подключение ИИ будет в блоке 2."
    )