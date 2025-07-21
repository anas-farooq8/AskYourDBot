import os
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.values.get("Body", "").strip()
    sender   = request.values.get("From")
    print(f"Received from {sender}: {incoming}")

    reply = "Hello, how can I help you today?"

    resp = MessagingResponse()
    resp.message(str(reply))
    return str(resp)

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug)
