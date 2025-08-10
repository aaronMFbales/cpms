"""
Enhanced Security Module for DTI CPMS
Implements strong password hashing, validation, and security utilities
"""

import bcrypt
import hashlib
import secrets
import string
import re
from typing import Tuple, Optional
import streamlit as st

def hash_password_secure(password: str) -> str:
    """
    Hash password using bcrypt with proper salt
    Much more secure than SHA-256
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # Higher rounds = more secure but slower
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password_secure(password: str, hashed: str) -> bool:
    """
    Verify password against bcrypt hash
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def validate_password_strength(password: str, username: str = "") -> Tuple[bool, str]:
    """
    Validate password meets security requirements
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for basic complexity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    # Check for common patterns
    if username and username.lower() in password.lower():
        return False, "Password cannot contain username"
    
    common_patterns = ['password', '123456', 'admin', 'user', 'login']
    if any(pattern in password.lower() for pattern in common_patterns):
        return False, "Password cannot contain common words"
    
    return True, "Password meets security requirements"

def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks
    """
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('..', '')
    return filename[:255]  # Limit length

def rate_limit_check(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """
    Simple rate limiting using session state
    Returns True if request is allowed, False if rate limited
    """
    import time
    
    current_time = time.time()
    rate_limit_key = f"rate_limit_{identifier}"
    
    if rate_limit_key not in st.session_state:
        st.session_state[rate_limit_key] = []
    
    # Clean old attempts outside the window
    window_seconds = window_minutes * 60
    st.session_state[rate_limit_key] = [
        attempt_time for attempt_time in st.session_state[rate_limit_key]
        if current_time - attempt_time < window_seconds
    ]
    
    # Check if under limit
    if len(st.session_state[rate_limit_key]) < max_attempts:
        st.session_state[rate_limit_key].append(current_time)
        return True
    
    return False

def secure_compare(a: str, b: str) -> bool:
    """
    Timing-safe string comparison to prevent timing attacks
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0

def validate_user_input(text: str, max_length: int = 500) -> str:
    """
    Basic input validation and sanitization
    """
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove potentially dangerous characters
    # Keep alphanumeric, spaces, and basic punctuation
    text = re.sub(r'[^\w\s\-.,@()]+', '', text)
    
    return text.strip()

# Migration functions for existing SHA-256 hashes
def is_bcrypt_hash(hash_string: str) -> bool:
    """
    Check if a hash is bcrypt format
    """
    return hash_string.startswith('$2b$') or hash_string.startswith('$2a$')

def migrate_password_hash(old_sha256_hash: str, password: str) -> Optional[str]:
    """
    Migrate from SHA-256 to bcrypt during login
    """
    # Verify the old hash first
    if hashlib.sha256(password.encode()).hexdigest() == old_sha256_hash:
        # Password is correct, create new bcrypt hash
        return hash_password_secure(password)
    return None
