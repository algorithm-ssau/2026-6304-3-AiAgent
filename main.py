from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from llm_client import classify_with_yandex_gpt

app = FastAPI(title="ИИ-агент техподдержки")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/classify")
async def classify(user_message: str = Form(...)):
    result = classify_with_yandex_gpt(user_message)
    return result