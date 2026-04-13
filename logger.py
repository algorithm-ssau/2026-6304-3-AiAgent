import csv
import os
from datetime import datetime
from typing import List, Dict

LOG_FILE = "requests_log.csv"

# Инициализация CSV-файла с заголовками, если его нет
def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "user_message", "category", "priority", "explanation"])

def log_request(user_message: str, result: dict):
    """Сохраняет запрос и ответ в CSV"""
    init_log()
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().isoformat(),
            user_message,
            result.get("category", ""),
            result.get("priority", ""),
            result.get("explanation", "")
        ])

def get_history(limit: int = 100) -> List[Dict]:
    """Возвращает последние записи (лимит) из лога"""
    init_log()
    rows = []
    with open(LOG_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    # возвращаем последние `limit` записей в обратном порядке (свежие сверху)
    return list(reversed(rows[-limit:]))

def log_error(error_message: str):
    """Записывает ошибки в отдельный файл error_log.txt"""
    with open("error_log.txt", mode='a', encoding='utf-8') as file:
        file.write(f"{datetime.now().isoformat()} - {error_message}\n")