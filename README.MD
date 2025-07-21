# Project Configuration Guide

This project leverages a `.env` file to securely manage sensitive configuration variables for seamless integration with Twilio, AskYourDatabase, Flask, and webhook services.

> **Note:** Never commit your actual `.env` file to version control. Use `.env.example` for reference and copy it to `.env` in your local environment.

---

## Table of Contents

1. [`.env` File Structure](#env-file-structure)
2. [Setup Instructions](#setup-instructions)
3. [Getting Started](#getting-started)
4. [Security Considerations](#security-considerations)

---

## `.env` File Structure

Populate your local `.env` file with the following variables:

```dotenv
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid       # Twilio Account SID for authentication
TWILIO_AUTH_TOKEN=your_twilio_auth_token         # Twilio Auth Token for secure API access
TWILIO_WHATSAPP_NUMBER=whatsapp:+xxxxxxxxxxx      # Sender WhatsApp number (Twilio)
TO_WHATSAPP_NUMBER=whatsapp:+xxxxxxxxxxx         # Recipient WhatsApp number

# AskYourDatabase API Configuration
ASKYOURDATABASE_CHAT_ID=your_chat_id             # Unique Chat ID for AskYourDatabase
ASKYOURDATABASE_API_KEY=your_api_key             # API Key for AskYourDatabase authentication
ASKYOURDATABASE_BASE_URL=https://www.askyourdatabase.com  # Base URL for API requests

# Flask Configuration
FLASK_ENV=development     # Flask environment (development/production)
FLASK_DEBUG=True          # Enable/disable debug mode
PORT=5000                 # Port for Flask server

# Webhook URL
WEBHOOK_URL=https://<your-webhook-url>/webhook  # URL for webhook handling
```

---

## Setup Instructions

Follow these steps to prepare your local environment:

1. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Getting Started

1. Copy `.env.example` to `.env` and update the values with your actual credentials.
2. Activate your virtual environment (see Step 2 above).
3. Install dependencies if you haven’t already (see Step 3 above).
4. Run the Flask application:

   ```bash
   flask run --port=$PORT
   ```

5. Your server should now be listening on `http://localhost:5000` (or the port you specified).

---

## Security Considerations

- **Never** commit your `.env` file to Git or any other version control.
- Share only the `.env.example` file with placeholders for sensitive values.
- Ensure access to production credentials is restricted to authorized personnel.

---
