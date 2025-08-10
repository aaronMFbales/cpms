"""
Security Logging and Monitoring System for DTI CPMS
Tracks security events, failed logins, and suspicious activities
"""

import os
import json
import datetime
from typing import Dict, Any, Optional
from enum import Enum
import streamlit as st

class SecurityEventType(Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED" 
    LOGIN_ATTEMPT_BLOCKED = "LOGIN_ATTEMPT_BLOCKED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACCOUNT_APPROVED = "ACCOUNT_APPROVED"
    ACCOUNT_REJECTED = "ACCOUNT_REJECTED"
    ACCOUNT_DELETED = "ACCOUNT_DELETED"
    INVALID_INPUT_DETECTED = "INVALID_INPUT_DETECTED"
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    FILE_UPLOADED = "FILE_UPLOADED"
    DATA_EXPORTED = "DATA_EXPORTED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    ADMIN_ACTION = "ADMIN_ACTION"

class SecurityLogger:
    def __init__(self):
        self.log_dir = "logs"
        self.security_log = os.path.join(self.log_dir, "security.log")
        self.failed_attempts_log = os.path.join(self.log_dir, "failed_attempts.log")
        self.audit_log = os.path.join(self.log_dir, "audit.log")
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Create logs directory with proper permissions"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, mode=0o700)
    
    def log_event(self, event_type: SecurityEventType, username: str = "", 
                  ip_address: str = "", details: str = "", additional_data: Dict[str, Any] = None):
        """Log security event with structured data"""
        
        timestamp = datetime.datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type.value,
            "username": username,
            "ip_address": ip_address,
            "details": details,
            "additional_data": additional_data or {}
        }
        
        # Write to appropriate log file
        if event_type in [SecurityEventType.LOGIN_FAILED, SecurityEventType.LOGIN_ATTEMPT_BLOCKED]:
            self._write_log(self.failed_attempts_log, log_entry)
        
        if event_type in [SecurityEventType.ADMIN_ACTION, SecurityEventType.ACCOUNT_APPROVED, 
                          SecurityEventType.ACCOUNT_REJECTED, SecurityEventType.ACCOUNT_DELETED]:
            self._write_log(self.audit_log, log_entry)
        
        # All events go to main security log
        self._write_log(self.security_log, log_entry)
    
    def _write_log(self, log_file: str, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            # If logging fails, try to write to a fallback location
            try:
                fallback_log = "security_fallback.log"
                with open(fallback_log, 'a', encoding='utf-8') as f:
                    f.write(f"LOGGING ERROR: {str(e)}\n")
                    f.write(json.dumps(log_entry) + '\n')
            except Exception:
                # If even fallback fails, we can't do much
                pass
    
    def get_failed_login_attempts(self, username: str, hours: int = 1) -> int:
        """Count failed login attempts for a user in the last N hours"""
        if not os.path.exists(self.failed_attempts_log):
            return 0
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        count = 0
        
        try:
            with open(self.failed_attempts_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        event_time = datetime.datetime.fromisoformat(entry['timestamp'])
                        
                        if (event_time > cutoff_time and 
                            entry['username'] == username and
                            entry['event_type'] == SecurityEventType.LOGIN_FAILED.value):
                            count += 1
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except FileNotFoundError:
            pass
        
        return count
    
    def get_recent_security_events(self, limit: int = 100) -> list:
        """Get recent security events for monitoring"""
        events = []
        
        if not os.path.exists(self.security_log):
            return events
        
        try:
            with open(self.security_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Get last N lines
                for line in lines[-limit:]:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return events
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log entries (keep last N days)"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for log_file in [self.security_log, self.failed_attempts_log, self.audit_log]:
            if not os.path.exists(log_file):
                continue
                
            try:
                # Read all entries
                entries = []
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            event_time = datetime.datetime.fromisoformat(entry['timestamp'])
                            if event_time > cutoff_time:
                                entries.append(entry)
                        except (json.JSONDecodeError, ValueError, KeyError):
                            continue
                
                # Write back filtered entries
                with open(log_file, 'w', encoding='utf-8') as f:
                    for entry in entries:
                        f.write(json.dumps(entry) + '\n')
                        
            except Exception:
                # If cleanup fails, don't break the app
                pass

# Global logger instance
security_logger = SecurityLogger()

# Helper functions for common logging scenarios
def log_login_attempt(username: str, success: bool, ip_address: str = "", details: str = ""):
    """Log login attempt"""
    if success:
        security_logger.log_event(
            SecurityEventType.LOGIN_SUCCESS, 
            username=username, 
            ip_address=ip_address,
            details=details
        )
    else:
        security_logger.log_event(
            SecurityEventType.LOGIN_FAILED,
            username=username,
            ip_address=ip_address, 
            details=details
        )

def log_admin_action(admin_username: str, action: str, target_username: str = "", details: str = ""):
    """Log administrative actions"""
    security_logger.log_event(
        SecurityEventType.ADMIN_ACTION,
        username=admin_username,
        details=f"Action: {action}, Target: {target_username}, Details: {details}"
    )

def log_data_access(username: str, action: str, sheet_name: str = "", details: str = ""):
    """Log data access and modifications"""
    security_logger.log_event(
        SecurityEventType.DATA_EXPORTED if "export" in action.lower() else SecurityEventType.ADMIN_ACTION,
        username=username,
        details=f"Data Action: {action}, Sheet: {sheet_name}, Details: {details}"
    )

def check_rate_limit(username: str, max_attempts: int = 5, hours: int = 1) -> bool:
    """Check if user has exceeded failed login rate limit"""
    failed_attempts = security_logger.get_failed_login_attempts(username, hours)
    return failed_attempts < max_attempts

def log_suspicious_activity(username: str, activity_type: str, details: str):
    """Log suspicious activities"""
    security_logger.log_event(
        SecurityEventType.SUSPICIOUS_ACTIVITY,
        username=username,
        details=f"Activity: {activity_type}, Details: {details}"
    )
