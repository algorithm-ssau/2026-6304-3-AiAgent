from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from llm_client import classify_with_yandex_gpt
from logger import log_request, get_history

app = FastAPI(title="ИИ-агент техподдержки")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/classify")
async def classify(user_message: str = Form(...)):
    result = classify_with_yandex_gpt(user_message)
    log_request(user_message, result)
    return result

@app.get("/history", response_class=HTMLResponse)
async def show_history():
    history = get_history(limit=50)
    rows = []
    for record in history:
        rows.append(f"""
        <tr>
            <td>{record['timestamp']}</td>
            <td>{record['user_message'][:100]}{'…' if len(record['user_message'])>100 else ''}</td>
            <td>{record['category']}</td>
            <td>{record['priority']}</td>
            <td>{record['explanation'][:150]}</td>
        </tr>
        """)
    table_rows = "\n".join(rows)
    with open("templates/history.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    html_content = html_template.replace("{{ table_rows }}", table_rows)
    return HTMLResponse(content=html_content)