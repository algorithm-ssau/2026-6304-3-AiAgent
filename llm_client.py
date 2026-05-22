import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

def get_gigachat_token():
    """Получает Access token для GigaChat (действует 30 мин)"""
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {AUTH_KEY}"
    }
    
    data = {
        "scope": "GIGACHAT_API_PERS"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Ошибка получения токена: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Исключение при получении токена: {e}")
        return None

def classify_with_yandex_gpt(user_message: str) -> dict:
    if not CLIENT_ID or not AUTH_KEY:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: нет CLIENT_ID или AUTH_KEY в .env"
        }
    
    # Получаем токен
    token = get_gigachat_token()
    if not token:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Ошибка: не удалось получить токен GigaChat. Проверьте ключи."
        }
    
    # Формируем промпт
    prompt = f"""Ты — ИИ-агент техподдержки. Классифицируй обращение пользователя.

Обращение: "{user_message}"

Категории: access (доступ/пароль), bug (ошибка/баг), payment (оплата), suggestion (предложение), other (другое).
Приоритет: high (не могу работать), medium (мешает, есть обход), low (вопрос/предложение).

Ответь ТОЛЬКО в формате JSON, без пояснений. Пример:
{{"category": "access", "priority": "high", "explanation": "Пользователь не может войти"}}
"""
    
    # Запрос к GigaChat API
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 250
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            model_text = result["choices"][0]["message"]["content"]
            
            # Очистка от markdown
            model_text = model_text.strip()
            if model_text.startswith("```") and model_text.endswith("```"):
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
        else:
            return {
                "category": "other",
                "priority": "low",
                "explanation": f"Ошибка GigaChat API: {response.status_code} - {response.text[:200]}"
            }
    except Exception as e:
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Ошибка при вызове GigaChat: {str(e)}"
        }