import os
import httpx
from typing import Dict, Any
from dotenv import load_dotenv
from huggingface_hub import model_info
import requests

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.sentiment_model = "seara/rubert-tiny2-russian-sentiment"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://disare.app",  # Your app's domain
            "X-Title": "Disare"  # Your app's name
        }
        self._check_model_availability()

    def _check_model_availability(self):
        """Проверка доступности модели"""
        try:
            info = model_info(self.sentiment_model, expand="inference")
            if info.inference is None:
                print(f"Внимание: Модель {self.sentiment_model} может быть недоступна")
            else:
                print(f"Модель {self.sentiment_model} доступна")
        except Exception as e:
            print(f"Ошибка при проверке модели: {str(e)}")

    async def get_chat_response(self, message: str, user_context: Dict[str, Any] = None) -> str:
        """Get AI response using OpenRouter API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3-opus-20240229",  # or another model of your choice
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are Disare, an AI mental health assistant focused on helping busy professionals 
                                reduce stress and improve their well-being. Provide personalized, empathetic responses 
                                that combine CBT techniques with practical advice for stress management, sleep improvement, 
                                and nutrition. Keep responses concise and actionable."""
                            },
                            {
                                "role": "user",
                                "content": message
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    return "I apologize, but I'm having trouble processing your request right now. Please try again later."
                    
        except Exception as e:
            print(f"Error in AI service: {str(e)}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment using Hugging Face Inference API (Russian model).
        Returns a score: positive=1, neutral=0, negative=-1 (weighted by confidence).
        """
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        api_url = f"https://api-inference.huggingface.co/models/{self.sentiment_model}"
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": text})
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                result = result[0]
            # Find the label with the highest score
            best = max(result, key=lambda x: x["score"])
            label = best["label"].lower()
            score = best["score"]
            if label == "positive":
                return 1 * score
            elif label == "negative":
                return -1 * score
            else:
                return 0
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0

    def interpret_sentiment_score(self, score: float) -> str:
        if score >= 0.7:
            return "Очень позитивное"
        elif score >= 0.2:
            return "Позитивное"
        elif score <= -0.7:
            return "Очень негативное"
        elif score <= -0.2:
            return "Негативное"
        else:
            return "Нейтральное"

ai_service = AIService() 