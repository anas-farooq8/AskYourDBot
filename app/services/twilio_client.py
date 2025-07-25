from twilio.rest import Client
from app.settings.config import Config
from app.utils.logger import get_logger

# Initialize the Twilio REST client with your Account SID and Auth Token
_twilio = Client(
    Config.TWILIO_ACCOUNT_SID,
    Config.TWILIO_AUTH_TOKEN
)
logger = get_logger(__name__)

def send_whatsapp_message(to: str, body: str):
    """
    Send a WhatsApp message via Twilio.

    Parameters:
      to (str): The recipient’s WhatsApp number in E.164 format, 
                prefixed by 'whatsapp:' (e.g. 'whatsapp:+923001234567').
      body (str): The text content of the message.

    Returns:
      MessageInstance: The Twilio message object representing the sent message.
    """
    try:
        message = _twilio.messages.create(
            # The Twilio‑enabled WhatsApp number configured in your account
            from_=f"whatsapp:{Config.TWILIO_FROM_NUMBER}",
            body=body,     # The message text to deliver
            to=to          # The destination WhatsApp number
        )
        logger.info(f"📤 Sent WhatsApp message to {to}: {len(body)} chars (SID: {message.sid})")
        return message
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message to {to}: {e}")
        raise
