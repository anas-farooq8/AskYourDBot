import os
from twilio.rest import Client

class WhatsAppBot:
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_  = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.client = Client(account_sid, auth_token)

    def send_message(self, to: str, body: str) -> str:
        """Send a plain-text WhatsApp message."""
        msg = self.client.messages.create(
            from_=self.from_,
            to=to,
            body=body
        )
        return msg.sid
