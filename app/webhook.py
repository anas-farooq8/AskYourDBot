import os
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from ask_database_client import AskDatabaseClient

load_dotenv()
app = Flask(__name__)

db_client = AskDatabaseClient()

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.values.get("Body", "").strip()
    sender   = request.values.get("From")
    print(f"Received from {sender}: {incoming}")

    try:
        result = db_client.ask(incoming)
        print("AskYourDatabase response:", result)
        # Prefer the AI’s human-readable answer, fallback to raw data
        reply = result.get("aiResponse") or result.get("data") or "No results."
    except Exception as e:
        print("Error querying AskYourDatabase:", e)
        reply = "Sorry, I couldn't understand your request."

    resp = MessagingResponse()
    resp.message(str(reply))
    return str(resp)

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug)
