from twilio.rest import Client
from app.settings.config import Config

_twilio = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, body: str):
    return _twilio.messages.create(
        from_=f"whatsapp:{Config.TWILIO_FROM_NUMBER}",
        body=body,
        to=to
    )