import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

def get_gigachat_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {AUTH_KEY}"
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception:
        return None

def classify_with_yandex_gpt(user_message: str) -> dict:
    if not CLIENT_ID or not AUTH_KEY:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Нет CLIENT_ID или AUTH_KEY в .env",
            "suggested_response": "Настройте API ключи в файле .env"
        }
    
    token = get_gigachat_token()
    if not token:
        return {
            "category": "other",
            "priority": "low",
            "explanation": "Не удалось получить токен GigaChat",
            "suggested_response": "Сервис временно недоступен, попробуйте позже."
        }
    
    prompt = f"""Ты — ИИ-агент техподдержки. Классифицируй обращение пользователя и предложи готовый ответ оператору.

Обращение: "{user_message}"

Категории: access (доступ/пароль), bug (ошибка/баг), payment (оплата), suggestion (предложение), other (другое).
Приоритет: high (не могу работать), medium (мешает, есть обход), low (вопрос/предложение).

Ответь ТОЛЬКО в формате JSON, без пояснений. Поля:
- category: одна из категорий
- priority: один из приоритетов
- explanation: краткое пояснение (1 предложение)
- suggested_response: готовый ответ пользователю (3-4 предложения, вежливо, с рекомендациями)

Пример ответа:
{{"category": "access", "priority": "high", "explanation": "Пользователь не может войти в аккаунт", "suggested_response": "Здравствуйте! Попробуйте сбросить пароль через форму восстановления. Если это не поможет, проверьте, не включён ли Caps Lock. Также рекомендуем очистить кэш браузера. Если проблема останется, напишите нам, пожалуйста, скриншот ошибки."}}
"""
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }
    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=60)
        if response.status_code == 200:
            result = response.json()
            model_text = result["choices"][0]["message"]["content"]
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
                "explanation": parsed.get("explanation", ""),
                "suggested_response": parsed.get("suggested_response", "Рекомендуем обратиться в службу поддержки.")
            }
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Ошибка GigaChat: {response.status_code}",
            "suggested_response": "Сервис временно недоступен, попробуйте позже."
        }
    except Exception as e:
        return {
            "category": "other",
            "priority": "low",
            "explanation": f"Ошибка: {str(e)}",
            "suggested_response": "Произошла техническая ошибка. Пожалуйста, повторите запрос."
        }