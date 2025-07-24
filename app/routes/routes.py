import threading
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse

from app.utils.twilio_validator import validate_twilio_request
from app.services.message_processor import process_incoming
from app.services.twilio_client import send_whatsapp_message

bp = Blueprint("whatsapp", __name__)

@bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    1) Validate the Twilio signature.
    2) Read incoming message & sender.
    3) Spawn a background thread to handle it.
    4) Return empty TwiML immediately.
    """
    validate_twilio_request()

    incoming = request.values.get("Body", "").strip()
    sender   = request.values.get("From")
    print(f"📥 Received from {sender}: {incoming}", flush=True)

    def background_task(body, to):
        result = process_incoming(body)
        reply  = result.get("aiResponse", "Sorry, no answer available.")
        send_whatsapp_message(to=to, body=reply)

    threading.Thread(
        target=background_task,
        args=(incoming, sender),
        daemon=True
    ).start()

    # Always return valid TwiML, even empty, to acknowledge receipt.
    return str(MessagingResponse())
