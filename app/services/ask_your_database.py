import requests
from app.settings.config import Config

class AskYourDatabaseClient:
    def __init__(self):
        if not (Config.AYD_API_KEY and Config.AYD_CHAT_ID):
            raise RuntimeError("Missing AYD config")
        self.url     = f"{Config.AYD_BASE_URL}/api/ask/api"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.AYD_API_KEY}"
        }

    def ask(self, question: str, return_all: bool = False) -> dict:
        payload = {
            "question":  question,
            "chatbotid": Config.AYD_CHAT_ID,
            "returnAll": return_all,
            "properties": {}
        }
        try:
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
        except requests.Timeout:
            return {"success": False, "error": "Timeout", "detail": "Request to AYD timed out"}
        except requests.HTTPError as e:
            return {"success": False, "error": "HTTPError", "detail": str(e)}
        j = resp.json()
        if j.get("error"):
            return {
                "success": False,
                "error": j["error"],
                "detail": j.get("detail", ""),
                "sql": j.get("sql")
            }
        return {
            "success":     True,
            "sql":         j.get("sql"),
            "executedSql": j.get("executedSql"),
            "aiResponse":  j.get("aiResponse", ""),
            "data":        j.get("data", [])
        }
