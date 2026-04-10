from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="ИИ-агент техподдержки")

# Вспомогательная функция для классификации (в Блоке 2 её перепишут)
def classify_with_llm(message: str) -> dict:
    """
    Сейчас это заглушка. В Блоке 2 здесь будет реальный вызов YandexGPT/GigaChat.
    """
    return {
        "category": "test",
        "priority": "low",
        "explanation": "Это временная заглушка. Подключение ИИ будет в блоке 2."
    }

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/classify")
async def classify(user_message: str = Form(...)):
    result = classify_with_llm(user_message)
    return result