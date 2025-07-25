# WhatsApp to AskYourDatabase Bot

A lightweight Flask webhook that integrates Twilio WhatsApp with AskYourDatabase using **session-based conversations** and **streaming responses**.

## Features

- **Session Management**: Each WhatsApp number maintains its own 7-day conversation session
- **Streaming Responses**: Uses SSE (Server-Sent Events) for efficient real-time responses
- **Auto Session Renewal**: Automatically handles expired sessions with 401 error recovery
- **Message Length Limiting**: Enforces WhatsApp character limits with truncation
- **Thread-Safe**: CSV-based session storage with proper concurrency handling
- **Minimal Dependencies**: Clean, efficient codebase with only essential libraries

## Architecture

```
├── run.py                          # Flask app entry point
├── requirements.txt                # Minimal dependencies (6 packages)
├── ayd_sessions.csv               # Auto-generated session storage
└── app/
    ├── __init__.py                # App factory
    ├── settings/config.py         # Environment configuration
    ├── utils/twilio_validator.py  # Twilio signature validation
    ├── services/
    │   ├── simple_ayd_client.py   # Streaming AYD client with session management
    │   ├── session_storage.py     # Thread-safe CSV session storage
    │   ├── message_processor.py   # Minimal message orchestration
    │   └── twilio_client.py       # Outbound WhatsApp messaging
    └── routes/routes.py           # Webhook endpoint with background processing
```

## How It Works

1. **Incoming Message**: WhatsApp message arrives at `/whatsapp` webhook
2. **Immediate Response**: Returns empty TwiML to Twilio (under 15s timeout)
3. **Background Processing**: Spawns thread to handle message with session context
4. **Session Management**: Gets or creates AYD session with 7-day access token
5. **Streaming Query**: Sends question to AYD streaming API, concatenates text chunks
6. **Reply**: Sends formatted response back via Twilio REST API

## Configuration

Create a `.env` file with the following variables:

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-domain.com/whatsapp

# AskYourDatabase
ASKYOURDATABASE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ASKYOURDATABASE_CHAT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# App Settings
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000
MAX_SMS_CHARS=1600
```

## Quick Setup

1. **Create and activate virtual environment**:

   **Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/macOS:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the application**:

   ```bash
   python run.py
   ```

5. **Set webhook in Twilio Console**:
   - Navigate to Messaging → Try it out → Send a WhatsApp message
   - Set webhook URL to: `https://your-domain.com/whatsapp`

## Session Management

- **Session Creation**: Automatic on first message from new WhatsApp number
- **Session Storage**: CSV file (`ayd_sessions.csv`) with thread-safe access
- **Session Expiry**: 7 days, automatically renewed on 401 errors
- **Session Cleanup**: Expired sessions removed automatically

## Error Handling

- **401 Errors**: Automatically creates new session and retries request
- **Timeouts**: 60-second timeout with user-friendly error message
- **Rate Limits**: Built-in request handling with proper error responses
- **Message Limits**: Automatic truncation to WhatsApp character limits

## Dependencies

```
flask==2.3.3          # Web framework
twilio==8.10.3         # WhatsApp messaging
python-dotenv==1.0.0   # Environment variables
sseclient-py==1.8.0    # Server-sent events for streaming
requests==2.31.0       # HTTP client
gunicorn==21.2.0       # Production WSGI server
```

## Security

- Twilio request signature validation
- Environment-based configuration
- No hardcoded credentials
- Thread-safe session management

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Or use the built-in Flask server by setting environment variables:

```bash
export FLASK_DEBUG=False
python run.py
```

## File Structure

### Core Files

- **`run.py`**: Application entry point that creates and runs the Flask app
- **`requirements.txt`**: Minimal dependency list for production deployment
- **`ayd_sessions.csv`**: Auto-generated CSV file storing WhatsApp-to-AYD session mappings

### Application Module (`app/`)

- **`__init__.py`**: Flask application factory function
- **`settings/config.py`**: Centralized configuration loaded from environment variables

### Services (`app/services/`)

- **`simple_ayd_client.py`**: Session-based AskYourDatabase client with streaming support
- **`session_storage.py`**: Thread-safe CSV-based session storage
- **`message_processor.py`**: Minimal message orchestration logic
- **`twilio_client.py`**: Outbound WhatsApp messaging via Twilio REST API

### Routes (`app/routes/`)

- **`routes.py`**: Flask blueprint with webhook endpoint and background processing

### Utilities (`app/utils/`)

- **`twilio_validator.py`**: Twilio request signature validation for security

## Environment Variables

| Variable                  | Description                                           | Required |
| ------------------------- | ----------------------------------------------------- | -------- |
| `TWILIO_ACCOUNT_SID`      | Your Twilio Account SID                               | Yes      |
| `TWILIO_AUTH_TOKEN`       | Your Twilio Auth Token                                | Yes      |
| `TWILIO_FROM_NUMBER`      | WhatsApp-enabled Twilio number                        | Yes      |
| `TWILIO_WEBHOOK_URL`      | Public webhook URL for incoming messages              | Yes      |
| `ASKYOURDATABASE_API_KEY` | AskYourDatabase API key                               | Yes      |
| `ASKYOURDATABASE_CHAT_ID` | AskYourDatabase chatbot ID                            | Yes      |
| `FLASK_DEBUG`             | Enable Flask debug mode (`True` or `False`)           | No       |
| `HOST`                    | Host to bind Flask app (default: `0.0.0.0`)           | No       |
| `PORT`                    | Port to bind Flask app (default: `5000`)              | No       |
| `MAX_SMS_CHARS`           | Max characters per WhatsApp message (default: `1600`) | No       |

## Development

For development with auto-reload:

**Windows:**

```bash
# Activate virtual environment first
venv\Scripts\activate

# Set environment variables and run
set FLASK_DEBUG=True
python run.py
```

**Linux/macOS:**

```bash
# Activate virtual environment first
source venv/bin/activate

# Set environment variables and run
export FLASK_DEBUG=True
python run.py
```

Use ngrok for local testing:

```bash
ngrok http 5000
# Set webhook URL in Twilio Console to: https://your-ngrok-url.ngrok.io/whatsapp
```
