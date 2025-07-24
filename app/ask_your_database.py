import os
import requests
from typing import Any, Dict, List, Optional

DEFAULT_TIMEOUT = 30  # seconds

class AskYourDatabaseClient:
    def __init__(self):
        self.base_url = ("https://www.askyourdatabase.com").rstrip("/")
        self.chat_id  = os.getenv("ASKYOURDATABASE_CHAT_ID")
        self.headers  = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('ASKYOURDATABASE_API_KEY')}"
        }
        if not (self.base_url and self.chat_id and self.headers["Authorization"].split()[-1]):
            raise RuntimeError("Missing one or more ASKYOURDATABASE_* env vars.")

    def ask(
        self,
        question: str,
        return_all: bool = False,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a question and return a normalized dict."""
        payload = {
            "question":   question,
            "chatbotid":  self.chat_id,
            "returnAll":  return_all,
            "properties": properties or {}
        }

        url = f"{self.base_url}/api/ask/api"
        resp = requests.post(url, json=payload, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        j = resp.json()

        # Error response from API
        if "error" in j:
            return {
                "success": False,
                "error": j.get("error"),
                "detail": j.get("detail"),
                "sql": j.get("sql"),
                "executedSql": j.get("executedSql"),
                "aiResponse": "",
                "data": []
            }

        # Success response
        return {
            "success":    j.get("success", False),
            "sql":        j.get("sql"),
            "executedSql": j.get("executedSql"),  # may be None
            "aiResponse": j.get("aiResponse") or "",
            "data":       j.get("data") or []
        }
