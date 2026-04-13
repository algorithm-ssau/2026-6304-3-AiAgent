import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

def classify_with_yandex_gpt(user_message: str) -> dict:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    # Проверка наличия ключей
    if not API_KEY:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не задан YANDEX_API_KEY. Проверьте файл .env"
        }
    if not FOLDER_ID:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не задан YANDEX_FOLDER_ID. Проверьте файл .env"
        }
    
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
        "messages": [{"role": "user", "text": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            error_msg = f"API вернул ошибку {response.status_code}. Проверьте интернет и ключи."
            return {
                "category": "other",
                "priority": "low",
                "explanation": error_msg
            }
        result = response.json()
        model_text = result["result"]["alternatives"][0]["message"]["text"]
        model_text = model_text.strip()
        # Удаляем обрамление в виде ``` ... ``` или ```json ... ```
        if model_text.startswith("```") and model_text.endswith("```"):
            # Убираем первую строку с ```
            lines = model_text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            model_text = "\n".join(lines).strip()
        parsed = json.loads(model_text)
        return {
            "category": parsed.get("category", "other"),
            "priority": parsed.get("priority", "low"),
            "explanation": parsed.get("explanation", "")
        }
    except requests.exceptions.Timeout:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: таймаут при подключении к YandexGPT. Проверьте интернет."
        }
    except requests.exceptions.ConnectionError:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: нет подключения к интернету или Yandex Cloud недоступен."
        }
    except json.JSONDecodeError:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не удалось распарсить ответ от ИИ. Попробуйте ещё раз."
        }
    except Exception as e:
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Неизвестная ошибка: {str(e)}"
        }