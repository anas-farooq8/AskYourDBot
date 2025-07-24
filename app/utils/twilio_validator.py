import os
from flask import request, abort
from twilio.request_validator import RequestValidator
from app.settings.config import Config

# Initialize Twilio RequestValidator with your Auth Token from config
_validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)

def validate_twilio_request():
    """
    Verify that incoming requests to your webhook endpoint genuinely originate
    from Twilio by checking the X-Twilio-Signature header against the expected
    signature generated from your configured webhook URL and the request parameters.
    Aborts with HTTP 403 if validation fails.
    """
    # Fetch the signature Twilio sent in the request headers
    signature = request.headers.get("X-Twilio-Signature", "")
    
    # Your publicly accessible webhook URL, must match what you configured in Twilio
    url = os.getenv("TWILIO_WEBHOOK_URL")
    
    # All POST/GET parameters Twilio sent, as a simple dict
    params = request.values.to_dict()
    
    # Log details for debugging (flush ensures it appears immediately)
    """
    print(
        f"🔑 Validating Twilio request:\n"
        f"    URL:       {url}\n"
        f"    Params:    {params}\n"
        f"    Signature: {signature}",
        flush=True
    )
    """
    
    # Perform the cryptographic check
    if not _validator.validate(url, params, signature):
        # Log failure and reject the request
        print("🚨 Invalid Twilio signature – aborting request", flush=True)
        abort(403, description="Invalid Twilio signature")
