from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from llm_client import classify_with_yandex_gpt
from logger import log_request, get_history
from stats import generate_category_chart, generate_priority_chart
import pandas as pd
import zipfile
import io
import base64

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

@app.get("/stats", response_class=HTMLResponse)
async def show_stats():
    category_img = generate_category_chart()
    priority_img = generate_priority_chart()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Статистика обращений</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; }}
            .chart {{ margin-bottom: 30px; text-align: center; }}
            img {{ max-width: 100%; height: auto; }}
            a {{ color: #007bff; text-decoration: none; }}
            .export-btn {{ 
                background: #28a745; 
                color: white; 
                padding: 8px 15px; 
                text-decoration: none; 
                border-radius: 5px;
                display: inline-block;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Статистика обращений</h1>
            
            <p style="text-align: center;">
                <a href="/export" class="export-btn">📥 Скачать отчёт (CSV + графики)</a>
            </p>
            
            <div class="chart">
                <h2>Распределение по категориям</h2>
                {f'<img src="data:image/png;base64,{category_img}" />' if category_img else '<p>Нет данных</p>'}
            </div>
            <div class="chart">
                <h2>Распределение по приоритетам</h2>
                {f'<img src="data:image/png;base64,{priority_img}" />' if priority_img else '<p>Нет данных</p>'}
            </div>
            <p><a href="/">← На главную</a> | <a href="/history">📜 История</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/export")
async def export_data():
    try:
        df = pd.read_csv("requests_log.csv", encoding='utf-8')
    except:
        df = pd.DataFrame(columns=["timestamp", "user_message", "category", "priority", "explanation"])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Только один CSV в кодировке Windows-1251 (для Excel)
        csv_win = io.BytesIO()
        df.to_csv(csv_win, index=False, encoding='windows-1251', errors='ignore')
        zip_file.writestr("requests_log.csv", csv_win.getvalue())

        # Графики
        cat_img = generate_category_chart()
        pri_img = generate_priority_chart()

        if cat_img:
            zip_file.writestr("category_chart.png", base64.b64decode(cat_img))
        if pri_img:
            zip_file.writestr("priority_chart.png", base64.b64decode(pri_img))

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=report.zip"}
    )