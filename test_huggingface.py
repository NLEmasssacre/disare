import os
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ
api_key = os.getenv("HUGGINGFACE_API_KEY")
if not api_key:
    print("Ошибка: HUGGINGFACE_API_KEY не найден в .env файле")
    exit(1)

# URL для русскоязычной модели
API_URL = "https://api-inference.huggingface.co/models/seara/rubert-tiny2-russian-sentiment"

# Заголовки для запроса
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Тестовые тексты
test_texts = [
    "Сегодня отличный день!",  # Позитивный на русском
    "Я в восторге!",          # Очень позитивный на русском
    "Мне грустно и плохо",    # Негативный на русском
    "Обычный день",           # Нейтральный на русском
]

# Анализируем каждый текст
for text in test_texts:
    print(f"\nАнализ текста: {text}")
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    
    if response.status_code == 200:
        result = response.json()
        print("Результат:", result)
    else:
        print("Ошибка:", response.status_code)
        print("Текст ошибки:", response.text) 