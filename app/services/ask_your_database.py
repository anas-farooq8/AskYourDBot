import requests
from app.settings.config import Config

class AskYourDatabaseClient:
    """
    Client for sending natural‐language questions to the AskYourDatabase API
    and parsing its JSON response into a standardized dict.
    """

    def __init__(self):
        # Ensure required AYD credentials are set
        if not (Config.AYD_API_KEY and Config.AYD_CHAT_ID):
            raise RuntimeError("Missing AYD config: check ASKYOURDATABASE_API_KEY and ASKYOURDATABASE_CHAT_ID")

        # Base endpoint for AskYourDatabase’s “ask” API
        self.url = f"{Config.AYD_BASE_URL}/api/ask/api"

        # Standard headers for JSON + bearer‑token auth
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.AYD_API_KEY}"
        }

    def ask(self, question: str, return_all: bool = False) -> dict:
        """
        Send `question` to AYD and return a dict with:
          - success: bool
          - sql: the original SQL AYD generated
          - executedSql: the SQL after parameter injection (if any)
          - aiResponse: AYD’s textual analysis or explanation
          - data: list of row‐dicts returned by the query
        On error, returns success=False with error details.
        """
        payload = {
            "question":  question,
            "chatbotid": Config.AYD_CHAT_ID,
            "returnAll": return_all,
            "properties": {}
        }

        try:
            # POST the question, timeout quickly if AYD is unresponsive
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=20)
            resp.raise_for_status()
        except requests.Timeout:
            return {
                "success": False,
                "error": "Timeout",
                "detail": "Request to AskYourDatabase timed out"
            }
        except requests.HTTPError as e:
            return {
                "success": False,
                "error": "HTTPError",
                "detail": str(e)
            }

        j = resp.json()

        # AYD can return its own error field
        if j.get("error"):
            return {
                "success": False,
                "error": j["error"],
                "detail": j.get("detail", ""),
                "sql": j.get("sql")
            }

        # Success: extract SQL, executed SQL, AI text, and tabular data
        return {
            "success":     True,
            "sql":         j.get("sql"),
            "executedSql": j.get("executedSql"),
            "aiResponse":  j.get("aiResponse", ""),
            "data":        j.get("data", [])
        }
