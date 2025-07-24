import threading
import time
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse

from app.utils.twilio_validator import validate_twilio_request
from app.services.gpt_client      import GPTClient
from app.services.message_processor import process_incoming
from app.services.twilio_client  import send_whatsapp_message
from app.settings.config         import Config

bp    = Blueprint("whatsapp", __name__)
gpt   = GPTClient()

@bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    validate_twilio_request()

    incoming = request.values.get("Body", "").strip()
    sender   = request.values.get("From")
    print(f"📥 Received from {sender}: {incoming}", flush=True)

    # 1) Classify first
    try:
        # time taken
        start_time = time.time()
        is_q = gpt.is_relevant_question(incoming)
        end_time = time.time()
        print(f"🔍 is_relevant_question = {is_q} in {end_time - start_time} seconds", flush=True)
    except Exception as e:
        print("❌ Classifier error:", e, flush=True)
        is_q = False

    resp = MessagingResponse()

    # 2a) If NOT relevant: reply immediately with the “help” text
    if not is_q:
        resp.message("Hi! Ask me about fabric stock or BOM.")
        return str(resp)

    # 2b) If relevant: send placeholder ACK and kick off background work
    resp.message("Thanks! I'm working on your request and will reply shortly.")
    twiml = str(resp)

    def background_work(body, to):
        try:
            result = process_incoming(body)
            reply  = result.get("aiResponse", "Sorry, no answer available.")
        except Exception as e:
            print("❌ Background error:", e, flush=True)
            reply = "Oops, something went wrong processing your request."
        send_whatsapp_message(to=to, body=reply[: Config.MAX_MSG_CHARS])

    threading.Thread(
        target=background_work,
        args=(incoming, sender),
        daemon=True
    ).start()

    return twiml
