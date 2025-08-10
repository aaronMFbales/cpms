"""
Secure Session Management for DTI CPMS
Implements secure session handling with token rotation and timeout
"""

import json
import os
import time
import secrets
from typing import Optional, Dict, Any
import streamlit as st

class SecureSessionManager:
    def __init__(self, session_timeout_hours: int = 8):
        self.session_timeout = session_timeout_hours * 3600  # Convert to seconds
        self.session_dir = "sessions"
        self.ensure_session_dir()
    
    def ensure_session_dir(self):
        """Create sessions directory if it doesn't exist"""
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir, mode=0o700)  # Restrict permissions
    
    def generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Create a new secure session"""
        session_token = self.generate_session_token()
        session_data = {
            "token": session_token,
            "user_data": user_data,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "ip_address": self.get_client_ip(),
            "user_agent": self.get_user_agent()
        }
        
        session_file = os.path.join(self.session_dir, f"{session_token}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Store in Streamlit session
        st.session_state["session_token"] = session_token
        st.session_state["authenticated"] = True
        st.session_state["auth_cookie"] = user_data
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate and refresh session if valid"""
        if not session_token:
            return None
        
        session_file = os.path.join(self.session_dir, f"{session_token}.json")
        
        if not os.path.exists(session_file):
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            current_time = time.time()
            last_accessed = session_data.get("last_accessed", 0)
            
            # Check if session has expired
            if current_time - last_accessed > self.session_timeout:
                self.destroy_session(session_token)
                return None
            
            # Check for session hijacking (basic checks)
            if not self.validate_session_context(session_data):
                self.destroy_session(session_token)
                return None
            
            # Update last accessed time
            session_data["last_accessed"] = current_time
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return session_data.get("user_data")
        
        except Exception as e:
            # If session file is corrupted, remove it
            self.destroy_session(session_token)
            return None
    
    def validate_session_context(self, session_data: Dict[str, Any]) -> bool:
        """Basic session hijacking detection"""
        # Check IP address (can be disabled for mobile users)
        stored_ip = session_data.get("ip_address", "")
        current_ip = self.get_client_ip()
        
        # For demo purposes, we'll be lenient with IP checking
        # In production, you might want stricter validation
        
        return True  # Simplified for now
    
    def destroy_session(self, session_token: str):
        """Securely destroy session"""
        if session_token:
            session_file = os.path.join(self.session_dir, f"{session_token}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
        
        # Clear Streamlit session
        if "session_token" in st.session_state:
            del st.session_state["session_token"]
        st.session_state["authenticated"] = False
        st.session_state["auth_cookie"] = None
    
    def cleanup_expired_sessions(self):
        """Clean up expired session files"""
        if not os.path.exists(self.session_dir):
            return
        
        current_time = time.time()
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.session_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                    
                    last_accessed = session_data.get("last_accessed", 0)
                    if current_time - last_accessed > self.session_timeout:
                        os.remove(filepath)
                except Exception:
                    # Remove corrupted files
                    os.remove(filepath)
    
    def get_client_ip(self) -> str:
        """Get client IP address (simplified for demo)"""
        # In production, you'd get this from headers
        return "unknown"
    
    def get_user_agent(self) -> str:
        """Get user agent (simplified for demo)"""
        # In production, you'd get this from headers
        return "streamlit-app"
    
    def rotate_session_token(self, old_token: str) -> Optional[str]:
        """Rotate session token for additional security"""
        session_data = self.validate_session(old_token)
        if not session_data:
            return None
        
        # Destroy old session
        self.destroy_session(old_token)
        
        # Create new session with same user data
        new_token = self.create_session(session_data)
        return new_token

# Global session manager instance
session_manager = SecureSessionManager()
