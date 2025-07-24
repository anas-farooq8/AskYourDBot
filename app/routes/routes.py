import threading                           # For running background tasks without blocking
import time                                # For timing operations and delays
from flask import Blueprint, request       # Flask Blueprint for routes and request object
from twilio.twiml.messaging_response import MessagingResponse  # To build TwiML replies

from app.utils.twilio_validator import validate_twilio_request
from app.services.gpt_client import GPTClient
from app.services.message_processor import process_incoming
from app.services.twilio_client import send_whatsapp_message
from app.settings.config import Config

# Create a Flask Blueprint for WhatsApp webhook routes
bp = Blueprint("whatsapp", __name__)

# Instantiate the GPT classifier/formatter client once at module load
gpt = GPTClient()

@bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    Main entrypoint for incoming WhatsApp messages.
    1) Validate request signature.
    2) Classify message intent.
    3a) If irrelevant, reply immediately.
    3b) If relevant, send an ACK and process in background.
    """
    # 1) Ensure the request really came from Twilio
    validate_twilio_request()

    # 2) Extract the message body and sender phone number
    incoming = request.values.get("Body", "").strip()
    sender = request.values.get("From")
    print(f"📥 Received from {sender}: {incoming}", flush=True)

    # 3) Classification: is this a fabric-stock/BOM question?
    try:
        start_time = time.time()
        is_q = gpt.is_relevant_question(incoming)
        duration = time.time() - start_time
        print(f"🔍 is_relevant_question = {is_q} in {duration:.2f}s", flush=True)
    except Exception as e:
        # If classifier errors out, default to non‑stock question
        print("❌ Classifier error:", e, flush=True)
        is_q = False

    # Prepare a Twilio MessagingResponse object
    resp = MessagingResponse()

    # 4a) If NOT relevant: send a quick help reply and return immediately
    if not is_q:
        resp.message("Hi! Ask me about fabric stock or BOM.")
        return str(resp)

    # 4b) If relevant: acknowledge receipt and will reply later
    resp.message("Thanks! I'm working on your request and will reply shortly.")
    twiml = str(resp)  # capture the ACK response now

    # Define the background task that does the heavy lifting
    def background_work(body, to):
        try:
            # Process the question (calls AYD + GPT formatting)
            result = process_incoming(body)
            reply = result.get("aiResponse", "Sorry, no answer available.")
        except Exception as e:
            # Catch any errors in background processing
            print("❌ Background error:", e, flush=True)
            reply = "Oops, something went wrong processing your request."

        # Send the final reply back via Twilio REST API
        send_whatsapp_message(to=to, body=reply[: Config.MAX_MSG_CHARS])

    # Launch the background task in a daemon thread
    threading.Thread(
        target=background_work,
        args=(incoming, sender),
        daemon=True
    ).start()

    # 5) Immediately return the ACK, actual reply comes later
    return twiml
