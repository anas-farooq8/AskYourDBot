import os
from whatsapp_client import WhatsAppBot
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    bot = WhatsAppBot()
    to_number = os.getenv('TO_WHATSAPP_NUMBER')

    # 1) send a simple “Hello”
    sid = bot.send_message(to=to_number, body="Hello")
    print("Sent plain message SID:", sid)
