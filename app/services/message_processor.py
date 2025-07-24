from app.services.simple_ayd_client import SessionBasedAYDClient

# Initialize session-based AYD client
session_ayd = SessionBasedAYDClient()

def process_incoming(phone_number: str, text: str) -> dict:
    """
    Process incoming WhatsApp message with session-based conversation support.
    Simple approach: just get the response and return it.
    """
    # Call AYD with session context
    result = session_ayd.ask_with_session(phone_number, text)
    
    return result
