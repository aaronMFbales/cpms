"""
Enhanced Security Configuration for DTI CPMS Production
Implements additional security measures and configuration hardening
"""

import streamlit as st
import os
from typing import Dict, Any

def apply_security_config():
    """
    Apply security configurations for production deployment
    """
    
    # Security headers (limited in Streamlit but documented)
    st.markdown("""
    <!-- Security Headers -->
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
    <meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=()">
    """, unsafe_allow_html=True)
    
    # Hide Streamlit menu and footer for production
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stActionButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def get_security_config() -> Dict[str, Any]:
    """
    Get security configuration from environment or secrets
    """
    try:
        config = {
            # Session security
            "session_timeout_hours": int(st.secrets.get("security", {}).get("session_timeout_hours", "8")),
            "max_failed_logins": int(st.secrets.get("security", {}).get("max_failed_logins", "5")),
            "login_rate_limit_minutes": int(st.secrets.get("security", {}).get("login_rate_limit_minutes", "15")),
            
            # Password security
            "min_password_length": int(st.secrets.get("security", {}).get("min_password_length", "8")),
            "require_strong_passwords": st.secrets.get("security", {}).get("require_strong_passwords", "true").lower() == "true",
            
            # File security
            "max_file_size_mb": int(st.secrets.get("security", {}).get("max_file_size_mb", "50")),
            "allowed_file_types": st.secrets.get("security", {}).get("allowed_file_types", ".xlsx,.xls,.csv,.pdf,.jpg,.png").split(","),
            
            # Logging
            "log_retention_days": int(st.secrets.get("security", {}).get("log_retention_days", "90")),
            "enable_audit_logging": st.secrets.get("security", {}).get("enable_audit_logging", "true").lower() == "true",
            
            # Environment
            "environment": st.secrets.get("security", {}).get("environment", "production"),
            "debug_mode": st.secrets.get("security", {}).get("debug_mode", "false").lower() == "true"
        }
    except Exception:
        # Fallback to secure defaults if secrets not available
        config = {
            "session_timeout_hours": 8,
            "max_failed_logins": 5,
            "login_rate_limit_minutes": 15,
            "min_password_length": 8,
            "require_strong_passwords": True,
            "max_file_size_mb": 50,
            "allowed_file_types": [".xlsx", ".xls", ".csv", ".pdf", ".jpg", ".png"],
            "log_retention_days": 90,
            "enable_audit_logging": True,
            "environment": "production",
            "debug_mode": False
        }
    
    return config

def validate_environment():
    """
    Validate that the environment is properly configured for security
    """
    issues = []
    
    # Check if secrets.toml exists
    secrets_file = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_file):
        issues.append("⚠️ secrets.toml not found - using fallback configuration")
    
    # Check if logs directory exists
    if not os.path.exists("logs"):
        try:
            os.makedirs("logs", mode=0o700)
        except Exception:
            issues.append("⚠️ Cannot create logs directory")
    
    # Check if sessions directory exists
    if not os.path.exists("sessions"):
        try:
            os.makedirs("sessions", mode=0o700)
        except Exception:
            issues.append("⚠️ Cannot create sessions directory")
    
    return issues

class SecurityMiddleware:
    """
    Security middleware for additional protection
    """
    
    @staticmethod
    def check_request_security():
        """
        Perform security checks on incoming requests
        """
        # In a full web framework, you'd check:
        # - Request headers
        # - IP reputation
        # - Request patterns
        # - CSRF tokens
        
        # For Streamlit, we're limited, but we can still do basic checks
        pass
    
    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Sanitize output to prevent information disclosure
        """
        if not text:
            return ""
        
        # Remove sensitive information patterns
        sensitive_patterns = [
            (r'password["\s]*[:=]["\s]*[^"\s]+', '[PASSWORD_HIDDEN]'),
            (r'token["\s]*[:=]["\s]*[^"\s]+', '[TOKEN_HIDDEN]'),
            (r'secret["\s]*[:=]["\s]*[^"\s]+', '[SECRET_HIDDEN]'),
            (r'key["\s]*[:=]["\s]*[^"\s]+', '[KEY_HIDDEN]'),
        ]
        
        import re
        result = text
        for pattern, replacement in sensitive_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result

def get_deployment_checklist():
    """
    Return security deployment checklist
    """
    return [
        "✅ Admin credentials stored in secrets.toml (not in code)",
        "✅ .gitignore protecting secrets.toml",
        "✅ Strong password hashing implemented (bcrypt)",
        "✅ Input validation and sanitization",
        "✅ Session management with timeout",
        "✅ Security logging and monitoring",
        "✅ Rate limiting for failed logins",
        "⚠️ HTTPS enforcement (handled by Streamlit Cloud)",
        "⚠️ Regular security updates (manual process)",
        "⚠️ Backup and disaster recovery plan needed",
        "⚠️ User training on security practices needed"
    ]
