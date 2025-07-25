from flask import request, abort
from twilio.request_validator import RequestValidator
from app.settings.config import Config
from app.utils.logger import get_logger

# Initialize Twilio RequestValidator with your Auth Token from config
_validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
logger = get_logger(__name__)

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
    url = Config.TWILIO_WEBHOOK_URL
    
    # All POST/GET parameters Twilio sent, as a simple dict
    params = request.values.to_dict()
    
    # Perform the cryptographic check
    if not _validator.validate(url, params, signature):
        # Log failure and reject the request
        logger.warning(f"🚫 Invalid Twilio signature from {request.remote_addr}")
        logger.debug(f"Expected URL: {url}, Signature: {signature[:20]}...")
        abort(403, description="Invalid Twilio signature")
    
    logger.debug("✅ Twilio signature validated successfully")
