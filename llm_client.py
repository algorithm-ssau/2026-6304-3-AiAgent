import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

def classify_with_yandex_gpt(user_message: str) -> dict:
    # Проверяем, что переменные окружения загружены
    if not API_KEY:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не задан YANDEX_API_KEY в файле .env"
        }
    if not FOLDER_ID:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не задан YANDEX_FOLDER_ID в файле .env"
        }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    # Самый простой и надёжный промпт
    prompt = f"""Ты — ИИ-агент техподдержки. Классифицируй обращение пользователя.

Обращение: "{user_message}"

Категории (выбери одну):
- access: проблемы с доступом, входом, паролем
- bug: ошибки, баги
- payment: оплата, возвраты
- suggestion: предложения
- other: всё остальное

Приоритет (выбери один):
- high: пользователь не может работать
- medium: мешает, но есть обход
- low: вопрос или предложение

Ответь ТОЛЬКО в формате JSON, без пояснений. Пример:
{{"category": "access", "priority": "high", "explanation": "Пользователь не может войти"}}
"""

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": 250
        },
        "messages": [
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    try:
        # Отправляем запрос
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Выводим статус и тело ответа для отладки
        print(f"HTTP Status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")  # первые 500 символов
        
        # Проверяем статус
        if response.status_code != 200:
            return {
                "category": "other",
                "priority": "low",
                "explanation": f"Ошибка API: {response.status_code} - {response.text[:200]}"
            }
        
        # Парсим JSON
        result = response.json()
        
        # Извлекаем текст ответа модели
        model_text = result["result"]["alternatives"][0]["message"]["text"]
        
        # Пробуем распарсить JSON из ответа
        try:
            # Ищем JSON в ответе (на случай, если модель добавила лишний текст)
            start = model_text.find('{')
            end = model_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = model_text[start:end]
                parsed = json.loads(json_str)
            else:
                parsed = json.loads(model_text)
            
            return {
                "category": parsed.get("category", "other"),
                "priority": parsed.get("priority", "low"),
                "explanation": parsed.get("explanation", "")
            }
        except json.JSONDecodeError as e:
            # Если модель вернула не JSON
            return {
                "category": "other",
                "priority": "low",
                "explanation": f"Модель вернула не JSON: {model_text[:200]}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Ошибка сети: {str(e)}"
        }
    except Exception as e:
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Неизвестная ошибка: {str(e)}"
        }