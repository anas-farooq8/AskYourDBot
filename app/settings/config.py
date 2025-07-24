import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask runtime mode: "production" or "development"
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    # Whether to enable Flask’s debugger
    DEBUG     = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Host and port for app.run()
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    # Maximum characters per WhatsApp message
    MAX_MSG_CHARS = int(os.getenv("MAX_SMS_CHARS", 4000))

    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

    # AskYourDatabase
    AYD_API_KEY  = os.getenv("ASKYOURDATABASE_API_KEY")
    AYD_CHAT_ID  = os.getenv("ASKYOURDATABASE_CHAT_ID")
    AYD_BASE_URL = "https://www.askyourdatabase.com"

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
