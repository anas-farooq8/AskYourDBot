import os
import json
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from ask_your_database import AskYourDatabaseClient

load_dotenv()
app = Flask(__name__)
db_client = AskYourDatabaseClient()

MAX_SMS_CHARS = 4000  # WhatsApp allows ~4096 chars; keep headroom

def format_data_rows(data: list) -> str:
    """
    Pretty-print list[dict] for WhatsApp/SMS. Skips empty values.
    Two newlines between rows.
    """
    rows = []
    for item in data:
        parts = [f"{k}: {v}" for k, v in item.items() if v not in (None, "", [])]
        if parts:
            rows.append("\n".join(parts))
    return "\n\n".join(rows)

def build_reply(result: dict) -> str:
    """
    Compose the reply text:
    - If success: AI text + formatted data (if any).
    - If error:   show error & detail.
    Truncate to MAX_SMS_CHARS.
    """
    if not result.get("success", False):
        # Error path
        err = result.get("error", "Unknown error")
        detail = result.get("detail", "")
        base = f"Error: {err}"
        if detail:
            base += f"\nDetail: {detail}"
        if result.get("sql"):
            base += f"\nSQL: {result['sql']}"
        return base[:MAX_SMS_CHARS]

    ai_text = (result.get("aiResponse") or "").strip()
    data    = result.get("data", [])
    if data:
        data_block = format_data_rows(data)
        combo = f"{ai_text}\n\n{data_block}".strip() if ai_text else data_block
    else:
        combo = ai_text or "No results found."

    # Truncate if too long
    if len(combo) > MAX_SMS_CHARS:
        combo = combo[:MAX_SMS_CHARS - 1] + "…"

    return combo

@app.route("/whatsapp", methods=["POST"])
def webhook():
    incoming = request.values.get("Body", "").strip()
    sender   = request.values.get("From")
    print(f"Received from {sender}: {incoming}")

    try:
        result = db_client.ask(incoming)
        print("AskYourDatabase response:", json.dumps(result, indent=2, ensure_ascii=False))
        reply = build_reply(result)
    except Exception as e:
        print("Error querying AskYourDatabase:", e)
        reply = "Sorry, I couldn't process your request. Please try again."

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host  = os.getenv("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=debug)