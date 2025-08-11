import streamlit as st
import json
import os
import time
import hashlib
import uuid
from datetime import datetime, timedelta

class SecureSessionManager:
    """Secure session manager with per-browser isolation"""
    
    def __init__(self):
        self.sessions_dir = "data/sessions"
        self.ensure_sessions_dir()
    
    def ensure_sessions_dir(self):
        """Ensure sessions directory exists"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
    
    def get_browser_id(self):
        """Generate unique browser/device ID"""
        # Use Streamlit's session ID and additional browser fingerprinting
        try:
            session_id = st.runtime.get_instance().get_session_id() if st.runtime.get_instance() else None
        except:
            session_id = None
        
        # If no session ID available, generate based on browser info
        if not session_id:
            # Fallback: use random UUID stored in session state
            if 'browser_id' not in st.session_state:
                st.session_state.browser_id = str(uuid.uuid4())
            session_id = st.session_state.browser_id
        
        return session_id
    
    def get_session_file_path(self):
        """Get the session file path for current browser"""
        browser_id = self.get_browser_id()
        return os.path.join(self.sessions_dir, f"session_{browser_id}.json")
    
    def save_session(self, session_data):
        """Save session data for current browser"""
        try:
            session_file = self.get_session_file_path()
            session_data['timestamp'] = time.time()
            session_data['browser_id'] = self.get_browser_id()
            session_data['created_at'] = datetime.now().isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_session(self):
        """Load session data for current browser"""
        try:
            session_file = self.get_session_file_path()
            if not os.path.exists(session_file):
                return None
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired (24 hours)
            current_time = time.time()
            if current_time - session_data.get('timestamp', 0) > 86400:
                self.clear_session()
                return None
            
            # Update timestamp for session extension
            session_data['timestamp'] = current_time
            session_data['last_accessed'] = datetime.now().isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return session_data
            
        except Exception as e:
            return None
    
    def clear_session(self):
        """Clear session for current browser"""
        try:
            session_file = self.get_session_file_path()
            if os.path.exists(session_file):
                os.remove(session_file)
            return True
        except:
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired session files"""
        try:
            current_time = time.time()
            for filename in os.listdir(self.sessions_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    filepath = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            session_data = json.load(f)
                        
                        # Remove sessions older than 24 hours
                        if current_time - session_data.get('timestamp', 0) > 86400:
                            os.remove(filepath)
                    except:
                        # Remove corrupted session files
                        try:
                            os.remove(filepath)
                        except:
                            pass
        except:
            pass
    
    def get_active_sessions_count(self):
        """Get count of active sessions"""
        try:
            count = 0
            current_time = time.time()
            for filename in os.listdir(self.sessions_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    filepath = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            session_data = json.load(f)
                        
                        # Count non-expired sessions
                        if current_time - session_data.get('timestamp', 0) <= 86400:
                            count += 1
                    except:
                        pass
            return count
        except:
            return 0

# Global session manager instance
session_manager = SecureSessionManager()
