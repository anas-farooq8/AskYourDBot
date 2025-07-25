import time
from app.services.simple_ayd_client import SessionBasedAYDClient
from app.utils.logger import get_logger

# Initialize session-based AYD client
session_ayd = SessionBasedAYDClient()
logger = get_logger(__name__)

def process_incoming(phone_number: str, text: str) -> dict:
    """
    Process incoming WhatsApp message with session-based conversation support.
    Simple approach: just get the response and return it.
    """
    logger.info(f"📱 Processing message from {phone_number}: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Call AYD with session context
    start = time.time()
    result = session_ayd.ask_with_session(phone_number, text)
    duration = time.time() - start
    
    logger.info(f"🔍 AYD call took {duration:.2f}s, success={result.get('success')}")
    
    return result
