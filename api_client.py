import requests
from typing import List, Dict
import logging
from config import AppConfig 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, config: AppConfig):
        self.config = config
        
    def generate_response(self, messages: List[Dict], model: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        try:
            response = requests.post(
                self.config.api_base,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            if 'response' in locals():
                logger.error(f"Response: {response.text}")
            return f"Error generating response: {str(e)}"