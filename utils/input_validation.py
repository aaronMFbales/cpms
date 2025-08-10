"""
Input Validation and Security Utilities for DTI CPMS
Protects against XSS, injection attacks, and malicious input
"""

import re
import html
import os
from typing import Dict, Any, List, Optional
import streamlit as st

class InputValidator:
    
    # Define allowed patterns for different input types
    PATTERNS = {
        'name': r'^[a-zA-Z\s\-\.\']{1,100}$',
        'username': r'^[a-zA-Z0-9_]{3,30}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^[\+]?[0-9\-\(\)\s]{7,20}$',
        'address': r'^[a-zA-Z0-9\s\-\.,#\/]{1,500}$',
        'business_name': r'^[a-zA-Z0-9\s\-\.\,&\']{1,200}$',
        'alphanumeric': r'^[a-zA-Z0-9\s]{1,100}$',
        'numeric': r'^[0-9]{1,20}$',
        'decimal': r'^[0-9]+\.?[0-9]*$',
        'date': r'^\d{2}\/\d{2}\/\d{4}$',
        'year': r'^(19|20)\d{2}$'
    }
    
    @staticmethod
    def sanitize_input(text: str, input_type: str = 'general') -> str:
        """
        Sanitize user input based on type
        """
        if not text:
            return ""
        
        # Convert to string and limit length
        text = str(text)[:1000]  # Hard limit to prevent huge inputs
        
        # HTML escape to prevent XSS
        text = html.escape(text)
        
        # Remove null bytes and other dangerous characters
        text = text.replace('\x00', '')
        
        # Type-specific sanitization
        if input_type == 'email':
            text = text.lower().strip()
        elif input_type == 'name':
            text = text.title().strip()
        elif input_type == 'phone':
            # Remove extra spaces and normalize
            text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    @staticmethod
    def validate_input(text: str, input_type: str) -> tuple:
        """
        Validate input against predefined patterns
        Returns (is_valid, error_message)
        """
        if not text:
            return False, f"{input_type.replace('_', ' ').title()} is required"
        
        # Check for basic security issues
        dangerous_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'onload=', r'onerror=',
            r'<iframe', r'<object', r'<embed', r'eval\(', r'document\.cookie',
            r'window\.location', r'alert\(', r'confirm\(', r'prompt\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Input contains potentially dangerous content"
        
        # Check against type-specific pattern
        if input_type in InputValidator.PATTERNS:
            if not re.match(InputValidator.PATTERNS[input_type], text):
                return False, f"Invalid {input_type.replace('_', ' ')} format"
        
        return True, ""
    
    @staticmethod
    def validate_form_data(form_data: Dict[str, Any], field_types: Dict[str, str]) -> tuple:
        """
        Validate entire form data
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        for field_name, field_value in form_data.items():
            if field_name in field_types:
                field_type = field_types[field_name]
                
                # Sanitize first
                sanitized_value = InputValidator.sanitize_input(str(field_value), field_type)
                form_data[field_name] = sanitized_value
                
                # Then validate
                is_valid, error_msg = InputValidator.validate_input(sanitized_value, field_type)
                if not is_valid:
                    errors.append(f"{field_name}: {error_msg}")
        
        return len(errors) == 0, errors

class FileUploadValidator:
    """
    Validates file uploads for security
    """
    
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.pdf', '.jpg', '.jpeg', '.png'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> tuple:
        """
        Validate uploaded file for security
        """
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file size
        if uploaded_file.size > FileUploadValidator.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {FileUploadValidator.MAX_FILE_SIZE // (1024*1024)}MB"
        
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in FileUploadValidator.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed types: {', '.join(FileUploadValidator.ALLOWED_EXTENSIONS)}"
        
        # Check for dangerous filenames
        dangerous_names = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in uploaded_file.name for char in dangerous_names):
            return False, "Filename contains dangerous characters"
        
        return True, ""

# Form validation helpers for specific DTI CPMS forms
class CPMSFormValidator:
    """
    Specific validation rules for CPMS forms
    """
    
    BUSINESS_OWNER_FIELDS = {
        'Name of Business Owner': 'name',
        'Address': 'address',
        'Contact Number': 'phone',
        'Email Address': 'email',
        'Gender': 'alphanumeric',
        'Age': 'numeric',
        'Position': 'alphanumeric',
        'Educational Attainment': 'alphanumeric'
    }
    
    CLIENT_FIELDS = {
        'Company Name': 'business_name',
        'Address': 'address',
        'Contact Person': 'name',
        'Position': 'alphanumeric',
        'Contact Number': 'phone',
        'Email Address': 'email',
        'Website': 'alphanumeric',
        'Nature of Business': 'business_name',
        'Business Classification': 'alphanumeric'
    }
    
    @staticmethod
    def validate_business_owner_form(form_data: Dict[str, Any]) -> tuple:
        """Validate Business Owner form specifically"""
        return InputValidator.validate_form_data(form_data, CPMSFormValidator.BUSINESS_OWNER_FIELDS)
    
    @staticmethod
    def validate_client_form(form_data: Dict[str, Any]) -> tuple:
        """Validate Client form specifically"""
        return InputValidator.validate_form_data(form_data, CPMSFormValidator.CLIENT_FIELDS)

# Security middleware for Streamlit
def apply_security_headers():
    """
    Apply security headers (limited in Streamlit, but we can try)
    """
    # This is mostly for documentation as Streamlit has limited header control
    st.markdown("""
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
    """, unsafe_allow_html=True)

def log_security_event(event_type: str, details: str, username: str = ""):
    """
    Log security events for monitoring
    """
    import datetime
    import os
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o700)
    
    log_file = os.path.join(log_dir, "security.log")
    timestamp = datetime.datetime.now().isoformat()
    
    log_entry = f"[{timestamp}] {event_type}: {details} (User: {username})\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        # If logging fails, don't break the app
        pass
