"""
Admin Configuration Module for DTI CPMS
Centralized admin account management with secure defaults
"""

import streamlit as st
import hashlib
import time

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_admin_config():
    """Get admin configuration from secrets or use secure defaults"""
    try:
        # Try to get from Streamlit secrets (production)
        admin_config = {
            "username": st.secrets.get("admin", {}).get("username", "admin"),
            "password": st.secrets.get("admin", {}).get("password", "dtidcfocpms2025"),
            "email": st.secrets.get("admin", {}).get("email", "admin@dti.gov.ph"),
            "first_name": st.secrets.get("admin", {}).get("first_name", "DTI"),
            "last_name": st.secrets.get("admin", {}).get("last_name", "Administrator")
        }
    except:
        # Fallback for local development
        admin_config = {
            "username": "admin",
            "password": "dtidcfocpms2025", 
            "email": "admin@dti.gov.ph",
            "first_name": "DTI",
            "last_name": "Administrator"
        }
    
    return admin_config

def get_default_admin_user():
    """Get default admin user structure"""
    config = get_admin_config()
    
    admin_user = {
        config["username"]: {
            "password": hash_password(config["password"]),
            "role": "admin",
            "approved": True,
            "created_at": time.time(),
            "email": config["email"],
            "first_name": config["first_name"],
            "last_name": config["last_name"],
            "is_default_admin": True
        }
    }
    
    return admin_user

def create_admin_if_not_exists(users_data):
    """Create admin user if it doesn't exist"""
    config = get_admin_config()
    admin_username = config["username"]
    
    # Check if any admin user exists
    has_admin = any(user_data.get("role") == "admin" for user_data in users_data.values())
    
    if not has_admin:
        # Create default admin
        default_admin = get_default_admin_user()
        users_data.update(default_admin)
        return True, f"Default admin '{admin_username}' created successfully!"
    
    return False, "Admin user already exists"

def get_admin_credentials_display():
    """Get admin credentials for display (for setup information)"""
    config = get_admin_config()
    return {
        "username": config["username"],
        "password": "••••••••••••••••" if len(config["password"]) > 8 else "••••••••",
        "email": config["email"],
        "name": f"{config['first_name']} {config['last_name']}"
    }

def validate_admin_password_strength(password):
    """Validate admin password meets security requirements"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets security requirements"
