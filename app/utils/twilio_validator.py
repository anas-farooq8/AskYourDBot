import os
from flask import request, abort
from twilio.request_validator import RequestValidator
from app.settings.config import Config

_validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)

def validate_twilio_request():
    signature = request.headers.get("X-Twilio-Signature", "")
    url       = os.getenv("TWILIO_WEBHOOK_URL")
    params    = request.values.to_dict()
    print(f"🔑 Validating Twilio request: {url} with params: {params} and signature: {signature}", flush=True)
    if not _validator.validate(url, params, signature):
        print("🚨 Invalid Twilio signature", flush=True)
        abort(403, description="Invalid Twilio signature")
