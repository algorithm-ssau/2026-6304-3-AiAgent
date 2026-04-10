from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="ИИ-агент техподдержки")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    """Отображает HTML-форму для ввода обращения"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/classify")
async def classify(user_message: str = Form(...)):
    """
    Временная заглушка. Позже заменим на вызов LLM.
    """
    return {
        "category": "test",
        "priority": "low",
        "explanation": "Это временная заглушка. Подключение ИИ будет в блоке 2."
    }