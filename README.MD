# AskYourDatabase WhatsApp Bot

A WhatsApp chatbot that connects to AskYourDatabase API for intelligent data queries using session-based conversations. Built with Flask and Twilio for seamless WhatsApp integration.

## Features

- **Session-Based Conversations**: Each WhatsApp number maintains its own 7-day conversation session for context continuity
- **Streaming API Integration**: Uses Server-Sent Events (SSE) for efficient real-time responses from AskYourDatabase
- **Auto Session Renewal**: Automatically handles expired sessions with 401 error recovery
- **WhatsApp Integration**: Seamless messaging through Twilio with 15-second webhook timeout compliance
- **Message Length Limiting**: Enforces WhatsApp's 1600 character limit with smart truncation
- **Thread-Safe Storage**: CSV-based session storage with proper concurrency handling
- **Rotating Logs**: 5MB log files with automatic rotation for production monitoring

## Architecture

The application follows a webhook-based architecture with background processing to handle Twilio's 15-second timeout requirement:

```
WhatsApp User → Twilio Webhook (15s timeout) → Flask App → Background Thread → AskYourDatabase API → Response
```

### Twilio Webhook Constraints

- **15-Second Timeout**: Twilio requires webhook responses within 15 seconds
- **Immediate TwiML Response**: App returns empty TwiML immediately to avoid timeout
- **Background Processing**: Database queries happen asynchronously in separate thread
- **Character Limit**: WhatsApp messages limited to 1600 characters maximum

### AskYourDatabase Integration

- **Session API**: Uses AskYourDatabase chatbot v2 session endpoints
- **Access Tokens**: 7-day session tokens stored locally with automatic renewal
- **Streaming Responses**: Real-time data streaming with text concatenation
- **Error Handling**: Robust retry logic for expired sessions and timeouts

## How It Works

### Complete Workflow

1. **Message Reception**: User sends WhatsApp message to Twilio number
2. **Webhook Call**: Twilio sends POST request to `/whatsapp` endpoint
3. **Immediate Response**: Flask returns empty TwiML within 15-second limit
4. **Background Thread**: Spawn background processing thread for database query
5. **Session Management**: Check for existing session or create new 7-day session
6. **Database Query**: Send question to AskYourDatabase streaming API
7. **Response Processing**: Concatenate streaming text chunks and format response
8. **Character Limit Check**: Ensure response fits within 1600 character limit
9. **WhatsApp Reply**: Send analysis back via Twilio REST API

### Session Management

1. **First Message**: Creates new session with phone number mapping
2. **Follow-up Messages**: Uses existing session for conversation continuity
3. **Session Expiry**: Automatically renews expired sessions (401 errors)
4. **Storage**: Thread-safe CSV storage with automatic cleanup

## Project Structure

```
AskYourDBot/
├── app/
│   ├── __init__.py              # Flask application factory with logging setup
│   ├── routes/
│   │   └── routes.py            # Webhook endpoint handler
│   ├── services/
│   │   ├── message_processor.py # Core message processing logic
│   │   ├── simple_ayd_client.py # AskYourDatabase session-based client
│   │   ├── session_storage.py   # CSV-based session management
│   │   └── twilio_client.py     # Twilio messaging service
│   ├── settings/
│   │   └── config.py            # Configuration management
│   └── utils/
│       ├── logger.py            # Rotating log system (5MB files)
│       └── twilio_validator.py  # Webhook signature validation
├── logs/                        # Application log files (auto-created)
├── ayd_sessions.csv            # Session storage (auto-created)
├── requirements.txt            # Python dependencies
├── run.py                     # Application entry point
└── README.md                  # This file
```

## Configuration

Create a `.env` file with the following variables:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-domain.com/whatsapp

# AskYourDatabase Configuration
ASKYOURDATABASE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ASKYOURDATABASE_CHAT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Flask Configuration
FLASK_ENV=production
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

## Dependencies

```
flask==2.3.3          # Web framework
twilio==8.10.3         # WhatsApp messaging
python-dotenv==1.0.0   # Environment variables
sseclient-py==1.8.0    # Server-sent events for streaming
requests==2.31.0       # HTTP client
gunicorn==21.2.0       # Production WSGI server
```
