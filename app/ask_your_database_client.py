import os
import requests
from dotenv import load_dotenv

class AskYourDatabaseClient:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("ASKYOURDATABASE_BASE_URL")
        self.chat_id  = os.getenv("ASKYOURDATABASE_CHAT_ID")
        self.headers  = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('ASKYOURDATABASE_API_KEY')}"
        }

    def ask(self, question: str, return_all: bool = False, properties: dict = None) -> dict:
        payload = {
            "question":   question,
            "chatbotid":  self.chat_id,
            "returnAll":  return_all,
            "properties": properties or {}
        }
        url = f"{self.base_url}/api/ask/api"
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()
