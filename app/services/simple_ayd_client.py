import requests
import json
import time
from sseclient import SSEClient
from typing import Dict, Optional
from app.settings.config import Config
from app.services.session_storage import CSVSessionStorage
from app.utils.logger import get_logger

class SessionBasedAYDClient:
    """
    Session-based AskYourDatabase client using streaming API with access tokens.
    Sessions last 7 days and are renewed on 401 errors.
    """
    
    def __init__(self):
        if not (Config.AYD_API_KEY and Config.AYD_CHAT_ID):
            raise RuntimeError("Missing AYD config: check ASKYOURDATABASE_API_KEY and ASKYOURDATABASE_CHAT_ID")
        
        self.base_url = Config.AYD_BASE_URL
        self.api_key = Config.AYD_API_KEY
        self.bot_id = Config.AYD_CHAT_ID
        
        # CSV-based session storage (stores access tokens with expiry)
        self.session_storage = CSVSessionStorage("ayd_sessions.csv")
        self.logger = get_logger(__name__)
        self.logger.info("🔧 SessionBasedAYDClient initialized")
    
    def _create_session(self, phone_number: str) -> Optional[str]:
        """
        Create a new AYD session and return access token.
        Returns access_token if successful, None otherwise.
        """
        try:
            self.logger.info(f"🆕 Creating new AYD session for {phone_number}")
            
            # Create session
            sess = requests.Session()
            resp = sess.post(
                f"{self.base_url}/api/chatbot/v2/session",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "chatbotid": self.bot_id,
                    "name": f"WhatsApp User {phone_number}",
                    "email": f"wa{phone_number.replace('+', '')}@example.com"
                }
            )
            resp.raise_for_status()
            
            callback_url = resp.json()["url"]
            self.logger.debug(f"✅ Got callback URL for {phone_number}")
            
            # Login to get access token
            login_resp = sess.get(callback_url, allow_redirects=True)
            login_resp.raise_for_status()
            
            access_token = sess.cookies.get("accessToken")
            if not access_token:
                self.logger.error(f"❌ No accessToken cookie found for {phone_number}")
                return None
            
            # Get expiry (7 days from creation) 
            expires_at = time.time() + (7 * 24 * 3600)  # 7 days
           
            # Store session
            success = self.session_storage.save_session(phone_number, access_token, expires_at)
            
            if success:
                self.logger.info(f"✅ Created and stored session for {phone_number}")
                return access_token
            else:
                self.logger.error(f"❌ Failed to store session for {phone_number}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error creating session for {phone_number}: {e}")
            return None
    
    def _get_or_create_session(self, phone_number: str) -> Optional[str]:
        """
        Get existing access token or create a new session.
        Returns access_token if successful, None otherwise.
        """
        # Try to get existing session
        session = self.session_storage.get_session(phone_number)
        if session:
            self.logger.info(f"📱 Using existing session for {phone_number}")
            return session['session_id']  # This is actually the access_token
        
        # Create new session if none exists or expired
        return self._create_session(phone_number)
    
    def ask_with_session(self, phone_number: str, question: str) -> Dict:
        """
        Send a question to AYD using session-based conversation with streaming response.
        Concatenates all text chunks and returns the complete response.
        """
        # Get or create access token
        access_token = self._get_or_create_session(phone_number)
        if not access_token:
            return {
                "success": False,
                "error": "SessionCreationFailed",
                "aiResponse": "Sorry, I couldn't establish a conversation session. Please try again."
            }
        
        # Send question with streaming
        try:
            sess = requests.Session()
            resp = sess.post(
                f"{self.base_url}/api/ask?debug=false",
                headers={
                    "Content-Type": "application/json",
                    "x-ayd-access-token": access_token,
                },
                json={
                    "question": question,
                    "fileUrls": [],
                    "botid": self.bot_id,
                    "debug": False
                },
                stream=True,
                timeout=60
            )
            
            # Handle 401 errors by recreating session
            if resp.status_code == 401:
                self.logger.info(f"🔄 Access token expired, creating new session for {phone_number}")
                self.session_storage.remove_session(phone_number)
                
                # Retry with new session
                access_token = self._create_session(phone_number)
                if not access_token:
                    return {
                        "success": False,
                        "error": "SessionRetryFailed",
                        "aiResponse": "Sorry, I'm having trouble maintaining our conversation. Please try again."
                    }
                
                # Retry the request
                resp = sess.post(
                    f"{self.base_url}/api/ask?debug=false",
                    headers={
                        "Content-Type": "application/json",
                        "x-ayd-access-token": access_token,
                    },
                    json={
                        "question": question,
                        "fileUrls": [],
                        "botid": self.bot_id,
                        "debug": False
                    },
                    stream=True,
                    timeout=60
                )
            
            resp.raise_for_status()
            
            # Process streaming response
            client = SSEClient(resp.iter_content(decode_unicode=False))
            text_parts = []
            
            for event in client.events():
                try:
                    data = json.loads(event.data)
                    
                    if data.get("isText"):
                        text_parts.append(data.get("content", ""))
                        
                except (ValueError, TypeError):
                    continue
            
            # Concatenate all text chunks
            full_response = "".join(text_parts).strip()
            
            if not full_response:
                full_response = "I processed your request but have no specific response to share."
            
            self.logger.info(f"✅ Got response for {phone_number}: {len(full_response)} chars")
            
            return {
                "success": True,
                "aiResponse": full_response
            }
            
        except requests.Timeout:
            self.logger.warning(f"⏰ Timeout for {phone_number}")
            return {
                "success": False,
                "error": "Timeout",
                "aiResponse": "Sorry, the request took too long. Please try again."
            }
        except Exception as e:
            self.logger.error(f"❌ Error for {phone_number}: {e}")
            return {
                "success": False,
                "error": "RequestFailed",
                "aiResponse": "Sorry, something went wrong. Please try again."
            }