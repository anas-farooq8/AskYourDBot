from twilio.rest import Client
from app.settings.config import Config

# Initialize the Twilio REST client with your Account SID and Auth Token
_twilio = Client(
    Config.TWILIO_ACCOUNT_SID,
    Config.TWILIO_AUTH_TOKEN
)

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
    return _twilio.messages.create(
        # The Twilio‑enabled WhatsApp number configured in your account
        from_=f"whatsapp:{Config.TWILIO_FROM_NUMBER}",
        body=body,     # The message text to deliver
        to=to          # The destination WhatsApp number
    )
