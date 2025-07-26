from twilio.rest import Client
from app.settings.config import Config
from app.utils.logger import get_logger

# Initialize the Twilio REST client with your Account SID and Auth Token
_twilio = Client(
    Config.TWILIO_ACCOUNT_SID,
    Config.TWILIO_AUTH_TOKEN
)
logger = get_logger(__name__)

def send_whatsapp_message(to: str, body: str):
    """
    Send a WhatsApp message via Twilio with automatic message splitting for long content.
    
    WhatsApp has a 1600 character limit per message. If the message is longer,
    it will be split into multiple messages with part indicators.

    Parameters:
      to (str): The recipient's WhatsApp number in E.164 format, 
                prefixed by 'whatsapp:' (e.g. 'whatsapp:+923001234567').
      body (str): The text content of the message.

    Returns:
      list: List of MessageInstance objects representing the sent messages.
    """
    try:
        max_chars = Config.MAX_MSG_CHARS
        
        # If message fits in one message, send normally
        if len(body) <= max_chars:
            message = _twilio.messages.create(
                from_=f"whatsapp:{Config.TWILIO_FROM_NUMBER}",
                body=body,
                to=to
            )
            logger.info(f"📤 Sent WhatsApp message to {to}: {len(body)} chars (SID: {message.sid})")
            return [message]
        
        # Split long message into chunks
        logger.info(f"📤 Message too long ({len(body)} chars), splitting into parts...")
        messages = []
        chunks = _split_message(body, max_chars)
        
        for i, chunk in enumerate(chunks, 1):
            # Add part indicator for multiple messages
            part_header = f"[Part {i}/{len(chunks)}]\n"
            chunk_with_header = part_header + chunk
            
            message = _twilio.messages.create(
                from_=f"whatsapp:{Config.TWILIO_FROM_NUMBER}",
                body=chunk_with_header,
                to=to
            )
            messages.append(message)
            logger.info(f"📤 Sent part {i}/{len(chunks)} to {to}: {len(chunk_with_header)} chars (SID: {message.sid})")
        
        logger.info(f"📤 Completed sending {len(chunks)} parts to {to}: total {len(body)} chars")
        return messages
        
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message to {to}: {e}")
        raise

def _split_message(text: str, max_chars: int) -> list:
    """
    Split a long message into chunks that respect WhatsApp's character limit.
    Tries to split at natural breakpoints (paragraphs, sentences) when possible.
    
    Args:
        text (str): The text to split
        max_chars (int): Maximum characters per chunk (accounting for part headers)
        
    Returns:
        list: List of text chunks
    """
    # Reserve space for part headers like "[Part 1/3]\n"
    header_space = 15
    chunk_limit = max_chars - header_space
    
    if len(text) <= chunk_limit:
        return [text]
    
    chunks = []
    remaining = text
    
    while remaining:
        if len(remaining) <= chunk_limit:
            chunks.append(remaining)
            break
        
        # Find the best split point within the limit
        split_point = chunk_limit
        
        # Try to split at paragraph breaks first (double newlines)
        paragraph_split = remaining.rfind('\n\n', 0, chunk_limit)
        if paragraph_split > chunk_limit * 0.6:  # Don't split too early
            split_point = paragraph_split + 2
        else:
            # Try to split at line breaks
            line_split = remaining.rfind('\n', 0, chunk_limit)
            if line_split > chunk_limit * 0.7:
                split_point = line_split + 1
            else:
                # Try to split at sentence boundaries
                sentence_split = remaining.rfind('. ', 0, chunk_limit)
                if sentence_split > chunk_limit * 0.7:
                    split_point = sentence_split + 2
                else:
                    # Try to split at word boundaries
                    word_split = remaining.rfind(' ', 0, chunk_limit)
                    if word_split > chunk_limit * 0.8:
                        split_point = word_split + 1
        
        chunk = remaining[:split_point].strip()
        chunks.append(chunk)
        remaining = remaining[split_point:].strip()
    
    return chunks
