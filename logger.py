import csv
import os
from datetime import datetime
from typing import List, Dict

LOG_FILE = "requests_log.csv"

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "user_message", "category", "priority", "explanation", "suggested_response"])

def log_request(user_message: str, result: dict):
    init_log()
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().isoformat(),
                user_message,
                result.get("category", ""),
                result.get("priority", ""),
                result.get("explanation", ""),
                result.get("suggested_response", "")
            ])
    except Exception as e:
        print(f"Ошибка логирования: {e}")

def get_history(limit: int = 100) -> List[Dict]:
    init_log()
    rows = []
    try:
        with open(LOG_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except Exception as e:
        print(f"Ошибка чтения лога: {e}")
    return list(reversed(rows[-limit:]))