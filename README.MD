## WhatsApp Business + AskYourDatabase Bot

A Flask-based webhook application that integrates Twilio's WhatsApp API with the AskYourDatabase HTTP API, using OpenAI for classification and formatting. Incoming WhatsApp messages are analyzed to determine relevance, forwarded to AskYourDatabase for SQL generation and query results, and then formatted into human-friendly replies.

---

### Project Structure

```
AskYourDBot/
├── requirements.txt       # Python dependencies
├── run.py                 # App entry point (WSGI server)
├── app/
│   ├── __init__.py        # Application factory
│   ├── settings/
│   │   └── config.py      # Config class reading .env
│   ├── utils/
│   │   └── twilio_validator.py  # Twilio request signature validation
│   ├── services/
│   │   ├── ask_your_database.py  # HTTP client for AskYourDatabase API
│   │   ├── gpt_client.py         # OpenAI classification & formatting
│   │   ├── message_processor.py  # Orchestrates classification, DB call, formatting
│   │   └── twilio_client.py      # Twilio REST API helper for outbound messages
│   ├── routes/
│       └── routes.py          # Flask blueprint defining the /whatsapp webhook
```

---

## Configuration Guide

All runtime configuration is managed via a `.env` file (copy `.env.example` to `.env`). **Never** commit your real `.env` to Git.

### .env.example

```dotenv
##### Twilio #####
TWILIO_ACCOUNT_SID=ACxxxxxxxx   # Your Twilio Account SID
TWILIO_AUTH_TOKEN=xxxxxxxxxxxx  # Your Twilio Auth Token
TWILIO_FROM_NUMBER=+xxxxxxxxxxx # WhatsApp-enabled Twilio number (E.164 format)
TWILIO_WEBHOOK_URL=https://your-ngrok-or-domain/whatsapp
                                 # Public webhook URL in Twilio Console
MAX_SMS_CHARS=4000              # Max characters per WhatsApp message (≤4096)

##### AskYourDatabase #####
ASKYOURDATABASE_CHAT_ID=xxxxxxx # AskYourDatabase chatbot ID
ASKYOURDATABASE_API_KEY=xxxxxxx # AskYourDatabase API key
ASKYOURDATABASE_BASE_URL=https://www.askyourdatabase.com
                                 # Base endpoint for API requests

##### OpenAI #####
OPENAI_API_KEY=sk-xxxxxxxxxxxxx # Your OpenAI API key

##### Flask #####
FLASK_ENV=development           # "development" or "production"
FLASK_DEBUG=True                # "True" to enable Flask’s debugger and auto-reload
HOST=0.0.0.0                    # Bind address for Flask
PORT=5000                       # Port to listen on
```

### Variable Descriptions

| Variable                     | Purpose                                                               |
| ---------------------------- | --------------------------------------------------------------------- |
| **FLASK_ENV**                | `development` enables debug & auto-reload; `production` disables them |
| **FLASK_DEBUG**              | `True` or `False`—toggles Flask debugger & reloader                   |
| **HOST**                     | IP/interface to bind Flask (e.g., `0.0.0.0`)                          |
| **PORT**                     | TCP port for Flask server                                             |
| **TWILIO_ACCOUNT_SID**       | Twilio account identifier                                             |
| **TWILIO_AUTH_TOKEN**        | Secret token for request validation & REST calls                      |
| **TWILIO_FROM_NUMBER**       | WhatsApp-enabled number, prefixed with `+` and E.164                  |
| **TWILIO_WEBHOOK_URL**       | Exact public URL (including `https://`) for incoming messages         |
| **MAX_SMS_CHARS**            | Maximum message length to send (WhatsApp cap \~4096 chars)            |
| **ASKYOURDATABASE_CHAT_ID**  | Identifier for your AskYourDatabase chatbot                           |
| **ASKYOURDATABASE_API_KEY**  | Secret key to authenticate AskYourDatabase requests                   |
| **ASKYOURDATABASE_BASE_URL** | Base URL for AskYourDatabase API                                      |
| **OPENAI_API_KEY**           | Secret key for OpenAI ChatCompletion API                              |

---

## Setup & Getting Started

1. **Clone the repository**

2. **Create & activate a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and fill in all required variables
   ```

5. **Run locally**

   - **Development** (auto-reload):

     ```bash
     export FLASK_ENV=development
     flask run --host=$HOST --port=$PORT
     ```

   - **Production**:

     ```bash
     export FLASK_ENV=production
     python run.py
     ```

6. **Expose to Twilio**

   - If local, start ngrok: `ngrok http $PORT`
   - Configure Twilio Console **Messaging → WhatsApp Sandbox** webhook to `https://<ngrok-id>.ngrok-free.app/whatsapp`

---

## Security Best Practices

- **Never** commit your real `.env` file.
- Use `.env.example` for placeholders.
- Restrict access to production secrets; consider a managed secrets vault.
- Rotate API keys and tokens regularly.

---
