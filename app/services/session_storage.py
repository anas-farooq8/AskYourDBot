import csv
import os
import time
from datetime import datetime
from typing import Optional, Dict
import threading

class CSVSessionStorage:
    """
    CSV-based session storage for WhatsApp phone number to AYD access token mapping.
    Thread-safe implementation with file locking for concurrent WhatsApp messages.
    """
    
    def __init__(self, csv_file_path: str = "sessions.csv"):
        self.csv_file_path = csv_file_path
        self.lock = threading.Lock()
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist."""
        try:
            if not os.path.exists(self.csv_file_path):
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['phone_number', 'session_id', 'expires_at', 'created_at'])
        except Exception:
            pass  # Fail silently, will be handled in individual operations
    
    def get_session(self, phone_number: str) -> Optional[Dict[str, str]]:
        """
        Retrieve session for a phone number if it exists and hasn't expired.
        Returns None if no valid session found.
        """
        if not phone_number:
            return None
            
        with self.lock:
            try:
                with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('phone_number') == phone_number:
                            # Check if session has expired
                            try:
                                expires_at = float(row['expires_at'])
                                if time.time() < expires_at:
                                    return {
                                        'phone_number': row['phone_number'],
                                        'session_id': row['session_id'],  # Actually access_token
                                        'expires_at': expires_at,
                                        'created_at': row['created_at']
                                    }
                                else:
                                    # Session expired, clean it up
                                    self._remove_session_unsafe(phone_number)
                                    break
                            except (ValueError, KeyError):
                                # Malformed row, skip
                                continue
                return None
            except (FileNotFoundError, PermissionError):
                return None
            except Exception:
                return None
    
    def save_session(self, phone_number: str, session_id: str, expires_at: float) -> bool:
        """
        Save or update session for a phone number.
        Returns True if successful, False otherwise.
        """
        with self.lock:
            try:
                # Remove existing session if any
                self._remove_session_unsafe(phone_number)
                
                # Add new session
                with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        phone_number,
                        session_id,
                        str(expires_at),
                        datetime.now().isoformat()
                    ])
                return True
            except Exception:
                return False
    
    def _remove_session_unsafe(self, phone_number: str):
        """
        Remove session for phone number. NOT thread-safe - must be called within lock.
        """
        try:
            # Read all rows except the one to remove
            rows_to_keep = []
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                if header:
                    rows_to_keep.append(header)
                    for row in reader:
                        if len(row) >= 4 and row[0] != phone_number:
                            rows_to_keep.append(row)
            
            # Write back the filtered rows
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows_to_keep)
        except Exception:
            pass  # Fail silently
    
    def remove_session(self, phone_number: str) -> bool:
        """
        Remove session for a phone number.
        Returns True if successful, False otherwise.
        """
        with self.lock:
            try:
                self._remove_session_unsafe(phone_number)
                return True
            except Exception:
                return False
