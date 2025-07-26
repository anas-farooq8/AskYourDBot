import time
from collections import defaultdict
from threading import Lock
from app.settings.config import Config

class SimpleRateLimiter:
    """
    Simple in-memory rate limiter for WhatsApp messages.
    Limits users to prevent abuse while allowing normal usage.
    """
    
    def __init__(self, max_requests_per_minute=Config.RATE_LIMITER_MAX_REQUESTS_PER_MINUTE):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if user is allowed to make a request.
        
        Args:
            user_id (str): User identifier (phone number)
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        current_time = time.time()
        
        with self.lock:
            # Clean old requests (older than 1 minute)
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if current_time - req_time < 60
            ]
            
            # Check if under limit
            if len(self.requests[user_id]) < self.max_requests:
                self.requests[user_id].append(current_time)
                return True
            
            return False
    
    def get_wait_time(self, user_id: str) -> int:
        """
        Get seconds until user can make next request.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            int: Seconds to wait, 0 if can request now
        """
        if not self.requests[user_id]:
            return 0
            
        oldest_request = min(self.requests[user_id])
        wait_time = 60 - (time.time() - oldest_request)
        return max(0, int(wait_time))

# Global rate limiter instance
rate_limiter = SimpleRateLimiter(max_requests_per_minute=Config.RATE_LIMITER_MAX_REQUESTS_PER_MINUTE)
