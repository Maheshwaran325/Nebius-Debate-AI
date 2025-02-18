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
            response.raise_for_status()  # This is good, keep it!

            # Check for empty responses *before* accessing ['choices']
            response_json = response.json()
            if not response_json.get('choices'):
                logger.warning(f"API returned an empty 'choices' array.  Full response: {response_json}")
                return "The AI model returned an empty response."

            if not response_json['choices'][0]['message']['content'].strip():
                logger.warning(f"API returned an empty message content. Full response: {response_json}")
                return "The AI model returned an empty response."

            return response_json['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:  # More specific exception
            logger.error(f"Request Exception: {e}")
            if 'response' in locals() and response: # Check if response exists
                logger.error(f"Response Status Code: {response.status_code}")
                logger.error(f"Response Text: {response.text}")
            return f"Error generating response: {e}"

        except Exception as e: #Catch any other error
            logger.error(f"An unexpected error occurred: {e}")
            if 'response' in locals() and response:
                logger.error(f"Response Status Code: {response.status_code}")
                logger.error(f"Response Text: {response.text}")
            return f"Error generating response: {e}"